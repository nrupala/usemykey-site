# Contributing

- Edit content in `site/` only. Never edit `dist/` (generated).
- Copy bar: plain words; one obvious next action per page; claim only
  behaviour that has shipped in the product repos. No absolute security
  claims ("unbreakable" and friends are banned — the Product Terms say
  there is no absolute security warranty).
- Before deploying: run `python3 tools/build_deploy.py build`, load the
  bundle locally, and check every route answers.
- After deploying: run `python3 tools/build_deploy.py verify` and do not
  call the deploy done unless the live pages pass.
- Commits use the account's noreply identity.
