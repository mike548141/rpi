- [ ] **Supply-chain: SHA-pin the workflow actions.** `release.yml` runs a third-party action by mutable tag inside
      the job holding `contents: write` + `id-token: write` — the credentials that sign the provenance attestations.
      Pin every `uses:` to a full commit SHA and enable Dependabot (`github-actions` ecosystem) to keep pins fresh;
      consider tightening the allowed-actions policy from "all" at the same time.
