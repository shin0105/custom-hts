/**
 * Typeahead search for Korean stocks by 6-digit code or Korean company name.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import { koreanMarketService } from '../services/koreanMarket';
import type { KoreanStockMasterItem } from '../types/korean';
import { formatMarketCapFrom100m } from '../utils/format';

interface SymbolSearchProps {
  /** Currently selected symbol. */
  value: string;
  /** Called with the chosen 6-digit code. */
  onSelect: (symbol: string, item?: KoreanStockMasterItem) => void;
  placeholder?: string;
  disabled?: boolean;
}

const MARKET_LABELS: Record<string, string> = {
  kospi: 'KOSPI',
  kosdaq: 'KOSDAQ',
  konex: 'KONEX',
};

const DEBOUNCE_MS = 200;

export const SymbolSearch: React.FC<SymbolSearchProps> = ({
  value,
  onSelect,
  placeholder = '종목명 또는 코드 검색 (e.g. 삼성전자, 005930)',
  disabled = false,
}) => {
  const [query, setQuery] = useState(value);
  const [results, setResults] = useState<KoreanStockMasterItem[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [highlighted, setHighlighted] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listboxId = 'symbol-search-listbox';

  // Keep the field in sync when the symbol changes elsewhere (URL, chips).
  useEffect(() => {
    setQuery(value);
  }, [value]);

  // Debounced search. The abort controller keeps a slow earlier response from
  // overwriting the results of a newer keystroke.
  useEffect(() => {
    const trimmed = query.trim();
    if (!open || trimmed === '') {
      setResults([]);
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await koreanMarketService.getStockMaster({
          query: trimmed,
          limit: 12,
          signal: controller.signal,
        });
        setResults(response.items);
        setHighlighted(0);
        setError(null);
      } catch (err) {
        if (axios.isCancel(err)) return;
        setResults([]);
        setError('종목 검색에 실패했습니다. Stock search failed.');
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }, DEBOUNCE_MS);

    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [query, open]);

  // Close on outside click.
  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const commit = (item: KoreanStockMasterItem) => {
    setQuery(item.symbol);
    setOpen(false);
    setResults([]);
    onSelect(item.symbol, item);
    inputRef.current?.blur();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setOpen(true);
      setHighlighted((prev) => Math.min(prev + 1, results.length - 1));
      return;
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setHighlighted((prev) => Math.max(prev - 1, 0));
      return;
    }
    if (event.key === 'Escape') {
      setOpen(false);
      return;
    }
    if (event.key === 'Enter') {
      event.preventDefault();
      const choice = results[highlighted];
      if (open && choice) {
        commit(choice);
      } else {
        // Allow a raw code to be submitted without picking from the list.
        const trimmed = query.trim();
        if (trimmed) {
          setOpen(false);
          onSelect(trimmed);
        }
      }
    }
  };

  const showDropdown = open && query.trim() !== '';

  const inputStyle: React.CSSProperties = useMemo(
    () => ({
      width: '100%',
      padding: '12px',
      fontSize: '16px',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      backgroundColor: disabled ? '#f3f4f6' : 'white',
    }),
    [disabled]
  );

  return (
    <div ref={containerRef} style={{ position: 'relative', flex: 1 }}>
      <input
        ref={inputRef}
        type="text"
        role="combobox"
        aria-expanded={showDropdown}
        aria-controls={listboxId}
        aria-autocomplete="list"
        aria-label="Korean stock symbol search"
        aria-activedescendant={
          showDropdown && results[highlighted]
            ? `symbol-option-${results[highlighted].symbol}`
            : undefined
        }
        placeholder={placeholder}
        value={query}
        disabled={disabled}
        onChange={(event) => {
          setQuery(event.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKeyDown}
        style={inputStyle}
      />

      {showDropdown && (
        <ul
          id={listboxId}
          role="listbox"
          aria-label="Search results"
          style={{
            position: 'absolute',
            top: 'calc(100% + 4px)',
            left: 0,
            right: 0,
            zIndex: 30,
            margin: 0,
            padding: 0,
            listStyle: 'none',
            maxHeight: '320px',
            overflowY: 'auto',
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 8px 24px rgba(15, 23, 42, 0.12)',
          }}
        >
          {loading && results.length === 0 && (
            <li style={{ padding: '12px', color: '#6b7280', fontSize: '14px' }}>
              검색 중… Searching…
            </li>
          )}

          {!loading && error && (
            <li style={{ padding: '12px', color: '#b91c1c', fontSize: '14px' }}>
              {error}
            </li>
          )}

          {!loading && !error && results.length === 0 && (
            <li style={{ padding: '12px', color: '#6b7280', fontSize: '14px' }}>
              검색 결과가 없습니다. No matching stocks.
            </li>
          )}

          {results.map((item, index) => {
            const isActive = index === highlighted;
            return (
              <li
                key={`${item.market}-${item.symbol}`}
                id={`symbol-option-${item.symbol}`}
                role="option"
                aria-selected={isActive}
                onMouseEnter={() => setHighlighted(index)}
                onMouseDown={(event) => {
                  // Fire before the input's blur so the click registers.
                  event.preventDefault();
                  commit(item);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px',
                  padding: '10px 12px',
                  cursor: 'pointer',
                  backgroundColor: isActive ? '#eff6ff' : 'white',
                  borderBottom: '1px solid #f3f4f6',
                }}
              >
                <span style={{ minWidth: 0 }}>
                  <span style={{ fontWeight: 600, fontSize: '14px' }}>
                    {item.name || item.symbol}
                  </span>
                  <span
                    style={{
                      marginLeft: '8px',
                      fontSize: '13px',
                      color: '#6b7280',
                      fontFamily: 'monospace',
                    }}
                  >
                    {item.symbol}
                  </span>
                </span>
                <span
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    flexShrink: 0,
                  }}
                >
                  <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                    {formatMarketCapFrom100m(item.market_cap_100m)}
                  </span>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#475569',
                      backgroundColor: '#f1f5f9',
                      borderRadius: '999px',
                      padding: '2px 8px',
                    }}
                  >
                    {MARKET_LABELS[item.market] ?? item.market.toUpperCase()}
                  </span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};
