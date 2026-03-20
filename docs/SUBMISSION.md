# Submission Checklist

Complete the following steps before submitting on Minerva.

## 1. Technical Report PDF

- Export `docs/technical-report.md` to `docs/technical-report.pdf`.
- Keep the final PDF within the module page limit.
- Include the Generative AI declaration as an appendix if the brief expects it inside the same PDF.
- Ensure the report still contains the correct repository and deployment links:
  - Repository: `https://github.com/John2968/book-insight-api`
  - Live API: `https://book-insight-api.onrender.com`
  - Live Swagger UI: `https://book-insight-api.onrender.com/api/v1/docs`

Example export command:

```bash
pandoc docs/technical-report.md -o docs/technical-report.pdf
```

## 2. Generative AI Declaration

- Include `docs/genai-declaration.md` in the submission, either inside the technical report PDF appendix or as a separate PDF if required.
- Add your name, student ID, signature, and date before exporting.
- Attach sample exported AI conversation logs if the module requires supplementary evidence.

## 3. API Documentation PDF

- Export `docs/api-documentation.md` to `docs/api-documentation.pdf`.
- Keep the exported file consistent with the deployed service and the final version of the code.

Example export command:

```bash
pandoc docs/api-documentation.md -o docs/api-documentation.pdf
```

## 4. Presentation Slides

- Prepare the PPTX slide deck for the oral presentation.
- Cover the required areas: project overview, architecture and data model, API documentation, version control, deployment, technical report highlights, GenAI usage, and final deliverables.
- Submit the PPTX directly on Minerva or upload it to a sharing platform and provide the link if the module asks for a hosted copy.

## 5. Repository Checks

- Keep the GitHub repository public and accessible.
- Make sure the repository contains the final source code, README, documentation files, and any exported PDFs you choose to include.
- Confirm that the deployed Render service still starts correctly.
- Confirm that the code in GitHub matches the version you describe in the report and slides.

## 6. Final Submission Pack

The final submission should normally include:

- Technical report PDF
- API documentation PDF
- PPTX presentation or presentation link, depending on the submission instructions
- Generative AI declaration
- Any required supplementary conversation-log evidence

---

Once those items are complete, the project is ready for submission.
