# Push a PRIVATE GitHub repository (MohammadAmanlou)

The repository is designed to be **private** because Constructor provided the original corpus and evaluation gold. The connected GitHub account was verified as `MohammadAmanlou` on 2026-10-19. The ChatGPT GitHub connector currently cannot create a new repository itself, so make the *empty private repo* once in the browser.

## One-time creation in the web UI

1. Go to https://github.com/new while logged into **MohammadAmanlou**.
2. Repository name: `constructor-ckl-research`. Description: `Private research assessment: evolving scientific knowledge hypergraphs`.
3. Select **Private**. Do **not** initialize README, .gitignore or license (they already exist in the ZIP).
4. Click **Create repository**. Copy the new repository URL, expected `https://github.com/MohammadAmanlou/constructor-ckl-research`.

## Push from extracted directory (Windows PowerShell)

Run from the directory containing **README.md, src/, research_lab/, outputs_selected/**:

```powershell
git --version
git init -b main
git status --short
git add .
git status --short
git commit -m "Research assessment: complete frozen experiments and selected method"
git remote add origin https://github.com/MohammadAmanlou/constructor-ckl-research.git
git push -u origin main
```

Git Credential Manager may open a browser to authenticate. **Never paste access tokens into ChatGPT or commit them**. If `origin` already exists, use `git remote -v` and `git remote set-url origin https://github.com/MohammadAmanlou/constructor-ckl-research.git` instead of running `git remote add origin` again.

**Before commit:** make sure `git status --short` does not contain `.venv/`, private personal messages, machine backup archives, `.env` or secrets. It **will** include `inputs/data.zip` and generated results: this is intentional only for a restricted **private** research archive; omit the supplied dataset if the employer forbids even private third-party storage.

## Verify online and connect ChatGPT

1. Open https://github.com/MohammadAmanlou/constructor-ckl-research and confirm the visibility says **Private**, plus `report.pdf`, `metrics.json`, `README.md`, `research_lab/`, and `outputs_selected/` exist.
2. GitHub is already connected to ChatGPT as `MohammadAmanlou`. If ChatGPT cannot read this new private repo, open ChatGPT **Settings > Plugins > GitHub** and grant the connector access to this specific repository (repo-level GitHub App permissions may require selection).
3. Share only the repository URL in the MMD Apply conversation, not credentials. ChatGPT can then inspect repository files and, when repository permissions permit, propose/push carefully reviewed changes.

For collaboration, work on a new branch and review a PR, rather than rewriting the locked baseline and `research_outputs/model_lock.json`. Proposed labeler v2 belongs on `feature/evidence-grounded-labeling` and should not retroactively alter confirmation.

## Employer delivery warning

Publishing to a GitHub **private** repository is **not** a submission to Constructor and does not confirm the supervisor got the files. A private link is inaccessible to an external evaluator without explicitly granting them access. Follow the original official assessment submission instructions; a ZIP attachment is often simpler than a private link. Check the due date independently.
