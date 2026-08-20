/**
 * Typeahead search for Korean stocks by 6-digit code or Korean company name.
 *
 * Users do not memorise 6-digit codes, so the field resolves 종목명 against the
 * KOSPI/KOSDAQ/KONEX master files rather than requiring an exact code.
 */

import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { koreanMarketService } from '../services/koreanMarket';
import type { KoreanStockMasterItem } from '../types/korean';
import { formatMarketCapFrom100m } from '../utils/format';
import { toUserMessage } from '../utils/apiError';
import { ko } from '../i18n/ko';
import { TextInput } from './ui';
import {
  color,
  fontSize,
  fontWeight,
  radius,
  shadow,
  space,
  zIndex,
} from '../theme/tokens';

interface SymbolSearchProps {
  /** Currently selected symbol. */
  value: string;
  /** Called with the chosen 6-digit code. */
  onSelect: (symbol: string, item?: KoreanStockMasterItem) => void;
  disabled?: boolean;
}

const MARKET_LABELS: Record<string, string> = {
  kospi: 'KOSPI',
  kosdaq: 'KOSDAQ',
  konex: 'KONEX',
};

const DEBOUNCE_MS = 200;
const LISTBOX_ID = 'symbol-search-listbox';

export const SymbolSearch: React.FC<SymbolSearchProps> = ({
  value,
  onSelect,
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

  // Keep the field in sync when the symbol changes elsewhere (URL, chips).
  useEffect(() => {
    setQuery(value);
  }, [value]);

  // Debounced search. The abort controller stops a slow earlier response from
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
        setError(toUserMessage(err, ko.stock.searchFailed));
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }, DEBOUNCE_MS);

    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [query, open]);

  // Close when focus moves outside the field.
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
        return;
      }
      // A raw code can still be submitted without picking from the list.
      const trimmed = query.trim();
      if (trimmed) {
        setOpen(false);
        onSelect(trimmed);
      }
    }
  };

  const showDropdown = open && query.trim() !== '';
  const activeOption = showDropdown ? results[highlighted] : undefined;

  const messageStyle: React.CSSProperties = {
    padding: space.md,
    color: color.inkDim,
    fontSize: fontSize.md,
  };

  return (
    <div ref={containerRef} style={{ position: 'relative', flex: 1, minWidth: 0 }}>
      <TextInput
        ref={inputRef}
        type="text"
        role="combobox"
        aria-expanded={showDropdown}
        aria-controls={LISTBOX_ID}
        aria-autocomplete="list"
        aria-label={ko.stock.searchPlaceholder}
        aria-activedescendant={
          activeOption ? `symbol-option-${activeOption.symbol}` : undefined
        }
        placeholder={ko.stock.searchPlaceholder}
        value={query}
        disabled={disabled}
        onChange={(event) => {
          setQuery(event.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKeyDown}
        style={{ width: '100%' }}
      />

      {showDropdown && (
        <ul
          id={LISTBOX_ID}
          role="listbox"
          aria-label={ko.stock.title}
          style={{
            position: 'absolute',
            top: 'calc(100% + 4px)',
            left: 0,
            right: 0,
            zIndex: zIndex.dropdown,
            margin: 0,
            padding: 0,
            listStyle: 'none',
            maxHeight: '320px',
            overflowY: 'auto',
            backgroundColor: color.surface,
            border: `1px solid ${color.border}`,
            borderRadius: radius.md,
            boxShadow: shadow.overlay,
          }}
        >
          {loading && results.length === 0 && (
            <li style={messageStyle}>{ko.stock.searchInProgress}</li>
          )}

          {!loading && error && (
            <li style={{ ...messageStyle, color: color.dangerInk }}>{error}</li>
          )}

          {!loading && !error && results.length === 0 && (
            <li style={messageStyle}>{ko.stock.searchNoResults}</li>
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
                  gap: space.md,
                  padding: `${space.sm} ${space.md}`,
                  cursor: 'pointer',
                  backgroundColor: isActive ? color.accentSoft : color.surface,
                  borderBottom: `1px solid ${color.borderSoft}`,
                }}
              >
                <span style={{ minWidth: 0 }}>
                  <span
                    style={{
                      fontWeight: fontWeight.semibold,
                      fontSize: fontSize.md,
                    }}
                  >
                    {item.name || item.symbol}
                  </span>
                  <span
                    className="hts-mono"
                    style={{
                      marginLeft: space.sm,
                      fontSize: fontSize.sm,
                      color: color.inkDim,
                    }}
                  >
                    {item.symbol}
                  </span>
                </span>
                <span
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: space.sm,
                    flexShrink: 0,
                  }}
                >
                  <span style={{ fontSize: fontSize.sm, color: color.inkDim }}>
                    {formatMarketCapFrom100m(item.market_cap_100m)}
                  </span>
                  <span
                    style={{
                      fontSize: fontSize.xs,
                      fontWeight: fontWeight.semibold,
                      color: color.inkMid,
                      backgroundColor: color.surfaceSunken,
                      borderRadius: radius.pill,
                      padding: `2px ${space.sm}`,
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
