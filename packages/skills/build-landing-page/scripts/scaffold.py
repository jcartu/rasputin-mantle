from __future__ import annotations

import html
import json
import sys


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    product = html.escape(str(data.get("product", "Your product")))
    audience = html.escape(str(data.get("audience", "teams")))
    cta = html.escape(str(data.get("cta", "Get started")))
    print(f"""<main>
  <section class=\"hero\">
    <p class=\"eyebrow\">Built for {audience}</p>
    <h1>{product} helps {audience} move faster.</h1>
    <p>Explain the primary outcome in one concrete sentence.</p>
    <a class=\"button\" href=\"#signup\">{cta}</a>
  </section>
  <section class=\"features\"><h2>Why it works</h2><ul><li>Benefit one</li><li>Benefit two</li><li>Benefit three</li></ul></section>
  <section class=\"faq\"><h2>FAQ</h2><p>Answer the top objection.</p></section>
</main>""")


if __name__ == "__main__":
    main()
