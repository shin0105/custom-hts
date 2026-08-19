/**
 * Turns a failed request into a sentence a user can act on.
 *
 * Axios messages ("Request failed with status code 500") say nothing about what
 * went wrong or what to do next, so they never reach the screen unmodified.
 */

import axios from 'axios';

const STATUS_MESSAGES: Record<number, string> = {
  400: '요청 조건을 확인해 주세요.',
  401: 'API 인증에 실패했습니다. 서버의 API 키 설정을 확인해 주세요.',
  403: 'API 접근 권한이 없습니다.',
  404: '조회 대상을 찾지 못했습니다.',
  429: '요청이 많아 잠시 후 다시 시도해 주세요.',
  500: '서버에서 데이터를 가져오지 못했습니다.',
  502: '데이터 제공처에 연결하지 못했습니다.',
  503: '데이터 제공처가 일시적으로 응답하지 않습니다.',
  504: '데이터 제공처 응답이 지연되고 있습니다.',
};

/**
 * @param fallback What to say when the failure carries no usable detail.
 */
export function toUserMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    // A `detail` from our own FastAPI layer is already written for a person.
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim() !== '') {
      return detail;
    }

    if (error.code === 'ERR_NETWORK') {
      return '서버에 연결하지 못했습니다. 백엔드가 실행 중인지 확인해 주세요.';
    }

    const status = error.response?.status;
    if (status && STATUS_MESSAGES[status]) {
      return `${fallback} (${STATUS_MESSAGES[status]})`;
    }
  }

  return fallback;
}
