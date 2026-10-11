FROM python:3.12-alpine@sha256:4c47124a8391cb7a9f571164147d154777cf012a4ece5f86097130d7a4478111

LABEL org.opencontainers.image.title="serendipity fake Vercel safe interpreter"
LABEL org.opencontainers.image.description="Offline, record-only harness for an inert public Skill document"

RUN mkdir -p /harness/shims /input /workspace /evidence \
    && chmod 0555 /harness /input \
    && chmod 0777 /workspace /evidence

COPY --chmod=0555 safe_interpreter.py /harness/safe_interpreter.py
COPY --chmod=0555 export_evidence.py /harness/export_evidence.py
COPY --chmod=0555 shim.py /harness/shims/curl
COPY --chmod=0555 shim.py /harness/shims/npm
COPY --chmod=0555 shim.py /harness/shims/npx
COPY --chmod=0555 shim.py /harness/shims/uname

ENV PATH="/harness/shims" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    EVIDENCE_DIR="/evidence"

WORKDIR /workspace
USER 65532:65532
ENTRYPOINT ["/usr/local/bin/python3", "/harness/safe_interpreter.py"]
