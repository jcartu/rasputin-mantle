declare module '@playwright/test' {
  export type Route = {
    fulfill(options: { status?: number; json?: unknown }): Promise<void>;
    request(): { postDataJSON(): unknown };
  };

  export type Page = {
    route(url: string, handler: (route: Route) => Promise<void>): Promise<void>;
    addInitScript(script: () => void): Promise<void>;
    goto(url: string): Promise<unknown>;
    addScriptTag(options: { path?: string; content?: string }): Promise<unknown>;
    evaluate<T>(fn: () => T): Promise<T>;
    evaluate<T, Arg>(fn: (arg: Arg) => T, arg: Arg): Promise<T>;
    locator(selector: string): { innerText(): Promise<string> };
  };

  type Matchers = {
    toBe(expected: unknown): void;
    toEqual(expected: unknown): void;
    toContain(expected: unknown): void;
    toMatchObject(expected: unknown): void;
  };

  type PollExpectation = {
    toBe(expected: unknown): Promise<void>;
  };

  export const expect: {
    (actual: unknown): Matchers;
    poll(callback: () => unknown): PollExpectation;
  };

  export const test: (
    name: string,
    callback: (fixtures: { page: Page }) => Promise<void> | void,
  ) => void;

  const playwright: {
    expect: typeof expect;
    test: typeof test;
  };

  export default playwright;
}

declare function require(moduleName: '@playwright/test'): typeof import('@playwright/test');
