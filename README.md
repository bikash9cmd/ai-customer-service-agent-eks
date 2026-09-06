# Building Production-Ready AI Agents on Amazon EKS

A hands-on collection of production-ready Agentic AI implementations built during the AWS BeSA Cohort 10 workshop.

This repository demonstrates different architectural patterns for building, deploying, observing, evaluating, and scaling AI agents on AWS using Amazon EKS and AWS managed AI services.

---

## Overview

Modern AI applications are moving beyond simple chatbots toward autonomous and collaborative AI agents capable of:

- Calling external tools
- Retrieving information from knowledge bases
- Maintaining conversational memory
- Collaborating with other agents
- Accessing external systems
- Evaluating their own performance
- Running production workloads on Kubernetes

This project explores these capabilities through multiple hands-on modules and real-world Agentic AI architectures.

---

# Architecture

The project explores two major Generative AI deployment strategies.

## 1. Self-Managed GenAI Strategy

In this architecture, the Large Language Model infrastructure is deployed and managed inside Amazon EKS.

```text
User
 │
 ▼
AI Agent
 │
 ▼
LiteLLM
 │
 ▼
vLLM
 │
 ▼
Qwen Language Model
 │
 ▼
Amazon EKS
