interface RuntimeWindow extends Window {
  __ROBO_BLOG_API_BASE_URL__?: string;
}

export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    const runtimeWindow = window as RuntimeWindow;
    if (runtimeWindow.__ROBO_BLOG_API_BASE_URL__) {
      return runtimeWindow.__ROBO_BLOG_API_BASE_URL__;
    }
  }

  return "http://localhost:8000";
}