export class BrowserNotAvailable extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BrowserNotAvailable";
  }
}

export class BrowserActionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BrowserActionError";
  }
}
