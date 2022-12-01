#!/bin/sh

if [ -z "${TESTING}" ]; then
    uvicorn app:app --host 0.0.0.0 --reload
else
    uvicorn app:app --host 0.0.0.0
fi
