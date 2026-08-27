# Getting listed

Installing the plugin is installing the product, so a listing is not marketing —
it is the install path. This is a half-day of clerical work that stays done,
not a campaign.

It is written down because the four destinations are gated on different things,
and doing them in the wrong order means advertising something broken.

## The sentence that does the work

```
claude mcp add --transport http tuckit https://app.tuckit.dev/mcp
```

A browser consent screen opens and that is the whole setup. **There is no token
to paste**, which is rare enough among public MCP servers to be the one
technical fact that makes a sceptical developer try it inside a minute. It
belongs at the top of every listing.

## MCP registry — can go now

`server.json` at the repository root is the submission. The endpoint is what is
being listed and the endpoint is not changing, so this does not wait on
anything.

Publishing needs a person: install `mcp-publisher`, authenticate (DNS for the
`dev.tuckit` namespace, or GitHub for a `io.github.*` one), then
`mcp-publisher publish`. The namespace has to be one we can prove we own.

Keep `version` in step with the Claude plugin's `plugin.json`. There are no git
tags in this repository; a release is a version bump.

## awesome-mcp lists — can go now

Same reasoning, same one-liner. A pull request each.

## Plugin marketplaces — wait

Claude Code, Codex and Antigravity. `.claude-plugin/marketplace.json` exists and
currently offers the Claude plugin.

Two things have to be true first, and both are about not advertising something
that is about to change or does not work:

- **The MCP tool surface and the workflow skills have to have settled.** Listing
  against tool names that are mid-replacement means promoting a broken install
  a week later.
- **Antigravity users need a way to install the workflow skills.** If the
  install instructions do not work, the listing has spent the first impression
  and there is no second one.

## While listing, fix the two things listings expose

- The README does not say that installing the Claude plugin is also how you get
  the workflow skills. A reader who wants them has no way to know they arrived.
- Do not write counts into prose. "N skills" in a sentence goes stale silently
  and nothing guards it — that has already happened more than once here.
