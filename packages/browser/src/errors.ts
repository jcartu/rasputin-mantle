export class BrowserNotAvailable extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BrowserNotAvailable";
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class BrowserActionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BrowserActionError";
    Object.setPrototypeOf(this, new.target.prototype);
  }
}
