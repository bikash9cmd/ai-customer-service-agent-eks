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
```

The model (Qwen2.5-3B) is served by vLLM on EKS, optionally on AWS Inferentia nodes, and LiteLLM exposes it through an OpenAI-compatible API that the agents call.

## 2. Integrated (AWS-managed) Strategy

In this architecture, the agents still run on Amazon EKS, but the model and the agent services are managed by AWS.

```text
User
 │
 ▼
Chat UI (Chainlit)
 │
 ▼
AI Agent on Amazon EKS (Strands Agents SDK)
 │
 ├──► Amazon Bedrock (foundation models)
 ├──► AgentCore Memory
 ├──► AgentCore Browser and Code Interpreter (managed tools)
 └──► AgentCore Evaluations
```

---

## Modules

Each module is a self-contained customer service agent (code, `Dockerfile` and Kubernetes manifest) that adds one capability on top of the previous one.

| Track | Module | What it adds |
|---|---|---|
| Self-managed | `200-strands-agents` | Basic Strands agent with tools, calling Qwen via LiteLLM |
| Self-managed | `300-observability-langfuse` | Tracing with Langfuse |
| Self-managed | `400-rag-milvus` | Retrieval-augmented generation with Milvus |
| Self-managed | `500-memory-milvus` | Conversational memory stored in Milvus |
| Self-managed | `600-agent-tools-mcp` | External tools through an MCP server |
| Self-managed | `700-multi-agent-a2a` | Multiple agents collaborating over the A2A protocol |
| Self-managed | `800-knowledge-graph` | Knowledge-graph retrieval with Neo4j |
| Integrated | `100-strands-bedrock` | Strands agent on Amazon Bedrock |
| Integrated | `200-observability-langfuse` | Langfuse tracing for the Bedrock agent |
| Integrated | `300-memory-agentcore` | Memory with AgentCore Memory |
| Integrated | `400-managed-tools` | AgentCore Browser and Code Interpreter |
| Integrated | `500-multi-agent-a2a` | A2A multi-agent system on managed services |
| Integrated | `550-evaluation-agentcore` | Agent evaluation with AgentCore Evaluations |
| UI | `modules/ui` | Chainlit chat UI with a dropdown to switch between agent profiles |

## Tech stack

| Area | Tools |
|---|---|
| Agents | Strands Agents SDK, A2A, MCP |
| Models | Qwen2.5-3B on vLLM, LiteLLM gateway, Amazon Bedrock |
| Platform | Amazon EKS, AWS Inferentia, Amazon ECR, AWS CodeBuild |
| Agent services | Amazon Bedrock AgentCore (Memory, Browser, Code Interpreter, Evaluations) |
| Data | Milvus (vectors), Neo4j (knowledge graph) |
| Observability | Langfuse |
| Infrastructure | Terraform, Kubernetes, Docker |
| UI | Chainlit |

## Repository structure

```text
terraform/        VPC, EKS cluster and add-ons, ECR, CodeBuild image pre-build,
                  LiteLLM, Langfuse, Neo4j, Inferentia, AgentCore resources
modules/
  20-self-managed/  Self-managed track (one folder per lab)
  30-integrated/    AWS-managed track (one folder per lab)
  ui/               Chainlit chat UI
```

## Getting started

### Prerequisites

- An AWS account with Amazon Bedrock model access
- Terraform, the AWS CLI v2 and `kubectl`
- An S3 bucket for Terraform state (the backend is `s3` with config supplied at init)

### 1. Provision the infrastructure

```bash
git clone https://github.com/bikash9cmd/ai-customer-service-agent-eks.git
cd ai-customer-service-agent-eks/terraform

terraform init \
  -backend-config="bucket=<your-state-bucket>" \
  -backend-config="key=ai-agents-eks/terraform.tfstate" \
  -backend-config="region=<your-region>"
terraform apply
```

Terraform creates the cluster and pre-builds the agent images in CodeBuild (no local Docker needed). Then point `kubectl` at the cluster with the command it prints:

```bash
terraform output -raw configure_kubectl | bash
```

### 2. Deploy an agent

Each module's `k8s.yaml` uses `${ACCOUNT_ID}` and `${AWS_REGION}` placeholders for the ECR image:

```bash
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=<your-region>

envsubst < ../modules/20-self-managed/200-strands-agents/customer-agent/k8s.yaml | kubectl apply -f -
envsubst < ../modules/ui/k8s.yaml | kubectl apply -f -
```

### 3. Clean up

The cluster, GPU/Inferentia nodes and load balancers are billable, so tear everything down when you're finished:

```bash
terraform destroy
```

## Acknowledgements

Built during the AWS BeSA (Become a Solutions Architect) Cohort 10 workshop.

## License

Released under the [MIT License](LICENSE).
