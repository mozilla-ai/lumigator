# Mozilla.ai Lumigator Helm chart

![Version: 0.1.2](https://img.shields.io/badge/Version-0.1.2-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: v0.1.2-alpha](https://img.shields.io/badge/Version-v0.1.2--alpha-informational?style=flat-square)

This Helm chart is the official way to deploy Lumigator in cloud environments with Kubernetes.

This Helm chart is composed by two sub-charts:

## `backend`

Deploys Lumigator core REST API, a Postgres instance and a minimal version of a Ray cluster.

## `frontend`

 Deploys Lumigator frontend, built with Vue 3, and Vite, and designed to interact with the REST API.
