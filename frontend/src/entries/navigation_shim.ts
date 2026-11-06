export function useSearchParams() {
  if (typeof window !== 'undefined') {
    return new URLSearchParams(window.location.search);
  }
  return new URLSearchParams();
}

export function useRouter() {
  return {
    push: (url: string) => {
      if (typeof window !== 'undefined') {
        window.location.href = url;
      }
    },
    replace: (url: string) => {
      if (typeof window !== 'undefined') {
        window.location.replace(url);
      }
    },
    back: () => {
      if (typeof window !== 'undefined') {
        window.history.back();
      }
    }
  };
}
