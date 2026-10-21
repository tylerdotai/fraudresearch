# Landing page acceptance contract

Specified before the page implementation. Run `bun run test:e2e` from site/.

Known failure modes: missing page; broken production base path/assets; mobile horizontal overflow; inaccessible controls; fake fraud/award claims; em dashes or emoji; decorative graphics mistaken for real findings; nonfunctional copy command; mobile menu inaccessible by keyboard; FAQ not using real shadcn primitives; automatic third-party tracking; private identifiers in source/build output.

Use real shadcn registry components. Test desktop and mobile views, axe accessibility, navigation, clipboard, FAQ, image loading, copy constraints, no automatic third-party requests, cookies or local storage. Preserve Playwright traces, screenshots, HTML report and JSON results privately. Do not publish raw test output. Test the production build and live Pages URL after deployment, not only the dev server.

The current design uses bold American colors, oversized type, a fictional eagle, a Nous-inspired adult character, a team illustration and a patriotic backdrop. The official Nous brand mark retains attribution; no endorsement is claimed. No government seals, fabricated metrics, fake user testimonials, glossy effects or implied official affiliation. No em dashes or emoji in rendered copy. External navigation is intentional; no tips, contact form, uploads or evidence collection.
