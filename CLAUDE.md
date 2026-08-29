# Working with Adam on this project

## Response style
- **Keep responses short.** Lead with the answer, cut the preamble.
- **One thing at a time.** Adam works sequentially — present one decision or one
  chunk of work per response, not a menu. Don't stack multiple open questions.
- Don't re-explain what's already in the week map.

## Project
14U hockey curriculum. See `14u-week-map.md` for the schedule and
`scripts/build_site.py` for the plan data.

**No roster, player, or team-specific information in this repo.** Skills and
drills only. Planning notes with team detail stay local and gitignored.

## Where things stand

- `docs/` is generated. Edit the data structures at the top of
  `scripts/build_site.py` (`WEEKS`, `THEMES`, `PRACTICE`, `AREAS`), then run
  `python3 scripts/build_site.py`. Never hand-edit `docs/`.
- Only the **Contact & Checking** area page is published. The other four are
  written but held back for review - flip `"published"` in `AREAS` to release one.
- Practices are logged from pasted IHS text, not scraped. See README.
- Push with the token in `.env` (gitignored):
  `AUTH=$(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64)`
  `git -c http.extraheader="AUTHORIZATION: Basic $AUTH" push origin main`

## Next up

Detail the **Contact & Checking** plan: the four-step progression, the fixed
5 min per-practice block, and drills for Weeks 1-3.
