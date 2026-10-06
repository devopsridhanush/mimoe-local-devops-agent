# mimOE Local DevOps Runbook Agent

A lightweight AI agent built using the **BYO Framework** approach with **mimOE Studio**, the **OpenAI Python SDK**, and a locally hosted `smollm-360m` model.

The goal of this project was to explore mimOE Studio, understand its local inference capabilities, connect to its OpenAI-compatible API, and build a small working AI agent that can be clearly explained and demonstrated.

---

## Overview

This project implements a small **DevOps Runbook Agent** that can answer focused troubleshooting questions related to:

- Docker
- Kubernetes
- Container restarts
- Kubernetes `CrashLoopBackOff`
- Basic operational troubleshooting commands

The agent communicates with a `smollm-360m` model loaded through mimOE Studio.

Instead of sending prompts to an external LLM provider, the application communicates with the OpenAI-compatible inference endpoint exposed by mimOE.

The final flow is:

```text
User
  |
  v
Python DevOps Agent
  |
  | OpenAI Python SDK
  |
  v
mimOE OpenAI-Compatible API
  |
  v
smollm-360m
  |
  v
Local inference on the mimOE runtime host
```

---

## Why I Built This

The purpose of this exercise was not to create a large production AI platform.

The main objectives were to demonstrate that I could:

1. Explore an unfamiliar AI platform.
2. Install and configure mimOE Studio.
3. Load and run a local language model.
4. Discover and test the inference API.
5. Connect an existing AI SDK to the mimOE endpoint.
6. Build a simple agent using the BYO Framework approach.
7. Handle runtime and resource-related issues.
8. Explain the design decisions and limitations clearly.

---

## Technology Stack

- **mimOE Studio**
- **mimOE Runtime**
- **smollm-360m**
- **Python 3**
- **OpenAI Python SDK**
- **python-dotenv**
- **PowerShell**
- **AWS EC2**
- **Git / GitHub**

---

## Development Environment

### Initial Local Development

I initially installed mimOE Studio on my Windows desktop.

The machine had approximately:

```text
8 GB RAM
Intel UHD Graphics 630
NVIDIA GTX 1650 Max-Q
```

During testing, the operating system had very little free memory available.

For example:

```text
Total RAM : ~7.85 GB
Free RAM  : ~1 GB
```

When attempting to load the model, mimOE returned errors such as:

```text
500 Internal Server Error

llama_model_load_from_file error:
unable to load model
```

I also observed cases where the runtime became unavailable after the failed load attempt.

To troubleshoot the issue, I validated:

- mimOE runtime availability
- port `8083`
- the model registry
- model download status
- available system memory
- network connectivity

The model registry confirmed that the model was downloaded successfully:

```text
Model      : smollm-360m
readyToUse : true
Size       : ~386 MB
```

This indicated that the problem was not model registration or download, but resource pressure during model loading.

---

## Why I Used AWS EC2

Because my desktop had limited available memory, I decided not to make the assignment dependent on an unstable local environment.

Instead, I used a Windows-based **AWS EC2 instance** with more available resources and installed mimOE Studio there.

This allowed me to:

- provide mimOE with sufficient memory,
- run the local mimOE runtime reliably,
- load `smollm-360m`,
- expose the inference endpoint,
- develop and test the Python agent,
- and complete the assignment without changing the overall architecture.

An important distinction is that the LLM inference is still performed by the **mimOE runtime itself**.

The application does not send prompts to OpenAI, Anthropic, or another external LLM API.

In the final development environment:

```text
AWS EC2 Windows Instance
        |
        +-- mimOE Studio
        |
        +-- mimOE Runtime
        |
        +-- smollm-360m
        |
        +-- Local OpenAI-compatible API
        |
        +-- Python DevOps Agent
```

Therefore, inference is local to the mimOE runtime host, although that host is an EC2 virtual machine rather than my physical laptop.

This was also a useful part of the exercise because it demonstrated that the application code was not tightly coupled to a specific physical machine.

---

## Architecture

```text
+--------------------------+
|          User            |
+------------+-------------+
             |
             v
+--------------------------+
|   Python DevOps Agent    |
|                          |
| - Topic selection        |
| - Runbook context        |
| - Error handling         |
| - Health check           |
+------------+-------------+
             |
             | OpenAI Python SDK
             |
             | HTTP
             v
+--------------------------+
|      mimOE Runtime       |
|                          |
| OpenAI-compatible API    |
| /mimik-ai/openai/v1      |
+------------+-------------+
             |
             v
+--------------------------+
|      smollm-360m         |
|                          |
| Local model inference    |
+--------------------------+
```

---

## mimOE API

After loading `smollm-360m` in mimOE Studio, the Model View exposed an OpenAI-compatible API.

The API follows the familiar OpenAI interface:

```text
POST /chat/completions
```

Example base URL:

```text
http://<MIMOE_HOST>:8083/mimik-ai/openai/v1
```

The application therefore uses the normal OpenAI Python client while changing the `base_url` to point to mimOE.

Example:

```python
from openai import OpenAI

client = OpenAI(
    base_url=MIMOE_BASE_URL,
    api_key=MIMOE_API_KEY,
)
```

The application then calls:

```python
client.chat.completions.create(...)
```

This was one of the most useful aspects of the integration because an application designed around an OpenAI-compatible interface can be redirected to mimOE without requiring a major rewrite.

---

## Why I Used the OpenAI Python SDK

I deliberately chose the standard OpenAI Python SDK instead of adding LangChain, CrewAI, or another orchestration framework.

The assignment was primarily about exploring and integrating mimOE.

Using the direct SDK provided several benefits:

- fewer dependencies,
- easier debugging,
- clear visibility into the mimOE integration,
- less abstraction,
- simple architecture,
- easier explanation during a technical interview.

A larger framework could be added later if orchestration, tools, RAG, or multi-agent workflows were required.

---

## Agent Design

The initial version of the application directly sent DevOps questions to `smollm-360m`.

That successfully proved that mimOE inference worked.

However, because `smollm-360m` is intentionally a very small model, unconstrained technical questions sometimes produced inaccurate answers.

Rather than hiding that limitation, I changed the design to use a small **grounded runbook architecture**.

The final flow is:

```text
User Question
      |
      v
Determine DevOps Topic
      |
      v
Select Trusted Runbook
      |
      v
Runbook + Question
      |
      v
smollm-360m through mimOE
      |
      v
Grounded Answer
```

The model is instructed to answer only from the supplied runbook.

This reduces hallucination and demonstrates an important AI engineering principle:

> A smaller local model can become more reliable when it is given focused, trusted context.

---

## Supported Runbooks

The current proof-of-concept includes runbooks for:

### Docker container restart troubleshooting

Example commands:

```bash
docker ps -a
docker logs --tail 100 <container-name>
docker inspect <container-name>
```

### Kubernetes CrashLoopBackOff troubleshooting

Example commands:

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous
```

The project intentionally keeps the knowledge base small because the objective is to demonstrate the mimOE integration rather than create a complete DevOps knowledge platform.

---

## Project Structure

```text
mimoe-local-devops-agent/
|
|-- agent.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md
|
`-- .venv/              # Local only, not committed
```

The real `.env` file is also excluded from Git.

---

## Configuration

Create a `.env` file from `.env.example`.

Example:

```env
MIMOE_BASE_URL=http://YOUR_MIMOE_HOST:8083/mimik-ai/openai/v1
MIMOE_API_KEY=YOUR_API_KEY
MIMOE_MODEL=smollm-360m
```

Do not commit the real `.env` file.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd mimoe-local-devops-agent
```

### 2. Create a Python virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure the environment

Copy `.env.example` to `.env` and update the mimOE endpoint values.

---

## mimOE Setup

Before running the Python application:

1. Start mimOE Studio.
2. Connect to the local/external mimOE runtime.
3. Open **AI Models**.
4. Load `smollm-360m`.
5. Open the model's **API** view.
6. Confirm the inference base URL.
7. Confirm the API key.
8. Keep the model loaded while running the Python agent.

---

## Verifying the mimOE Runtime

On Windows, the runtime can be checked with PowerShell:

```powershell
Test-NetConnection localhost -Port 8083
```

A healthy runtime should return:

```text
TcpTestSucceeded : True
```

The model registry can also be queried to confirm that the model is available.

Example:

```powershell
$headers = @{
    Authorization = "Bearer <API_KEY>"
}

Invoke-RestMethod `
    -Uri "http://localhost:8083/mimik-ai/store/v1/models" `
    -Method GET `
    -Headers $headers
```

The expected model status is:

```text
readyToUse : true
```

---

## Direct API Validation

Before writing the Python agent, I validated the mimOE API directly using PowerShell.

Example:

```powershell
$headers = @{
    "Authorization" = "Bearer <API_KEY>"
    "Content-Type"  = "application/json"
}

$body = @{
    model = "smollm-360m"
    messages = @(
        @{
            role = "user"
            content = "Explain Docker in two short sentences."
        }
    )
    stream = $false
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
    -Uri "http://<MIMOE_HOST>:8083/mimik-ai/openai/v1/chat/completions" `
    -Method POST `
    -Headers $headers `
    -Body $body

$response.choices[0].message.content
```

This confirmed that the client, mimOE API, and local model inference path were working before introducing additional application logic.

---

## Running the Agent

Start the application:

```powershell
python .\agent.py
```

Example:

```text
============================================================
 mimOE Local DevOps Runbook Agent
============================================================

Model    : smollm-360m
Endpoint : http://<MIMOE_HOST>:8083/mimik-ai/openai/v1

Grounded topics:
  - Docker
  - Kubernetes

Commands:
  /health
  /clear
  /topics
  /exit
```

---

## Health Check

The agent includes a `/health` command.

Example:

```text
Checking local mimOE inference...

mimOE status : Connected
Model        : smollm-360m
Inference    : Local
```

This confirms that the Python application can communicate with the mimOE inference endpoint.

---

## Example Interaction

```text
You:
A Docker container keeps restarting. What should I check?

Agent:
1. Check the container status:
   docker ps -a

2. Review recent logs:
   docker logs --tail 100 <container-name>

3. Inspect the container:
   docker inspect <container-name>
```

Another example:

```text
You:
Explain Kubernetes CrashLoopBackOff.

Agent:
CrashLoopBackOff means that a container repeatedly starts,
fails, and is restarted by Kubernetes.

Useful troubleshooting commands include:

kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous
```

---

## Error Handling

The application handles common failure conditions.

For example, if mimOE is unavailable:

```text
Unable to connect to mimOE.

Make sure:
1. mimOE Studio is running.
2. The local runtime is connected.
3. smollm-360m is loaded.
4. The endpoint in .env matches Studio.
```

This is more useful to the user than exposing a raw Python connection exception.

---

## Troubleshooting Experience

One of the useful parts of this exercise was troubleshooting the initial model-loading problem.

I used PowerShell to validate the runtime process, runtime port, model registry, available RAM, and network connectivity. This allowed me to distinguish between network problems, runtime problems, model-download problems, and host-resource limitations.

That troubleshooting eventually led to moving the development environment to a better-resourced EC2 instance.

---

## Security Considerations

The project follows some basic security practices:

- `.env` is excluded from Git.
- API configuration is not hard-coded in the Python source.
- `.env.example` contains only example configuration.
- The Python virtual environment is excluded from the repository.
- The agent does not execute commands supplied by the language model.
- DevOps commands are presented as recommendations only.

For a production environment I would also add proper secrets management, authentication, network restrictions, TLS, structured audit logging, input validation, and stronger authorization controls.

---

## Current Limitations

This is intentionally a small proof-of-concept.

Current limitations include:

- `smollm-360m` is a small model.
- The agent currently supports only a small set of DevOps topics.
- Runbooks are stored directly in Python.
- There is no vector database.
- There is no dynamic RAG pipeline.
- The agent does not execute infrastructure commands.
- There is no web UI.
- Conversation memory is intentionally minimal.
- EC2 was used as the runtime host because of resource limitations on the original desktop.

These trade-offs were intentional to keep the assignment focused.

---

## Future Improvements

Given more time, I would consider:

1. Moving runbooks into separate Markdown or JSON files.
2. Adding semantic retrieval over a larger runbook library.
3. Supporting additional topics such as AWS, Terraform, CI/CD, Linux, and networking.
4. Adding streaming responses.
5. Using the mimOE traceable inference endpoint for observability.
6. Adding structured logging.
7. Adding automated tests.
8. Adding a lightweight web interface.
9. Evaluating a larger local model when hardware resources permit.
10. Comparing local execution across laptop, edge device, and cloud VM environments.

---

## Key Design Decisions

### Why BYO Framework?

It provided the simplest way to integrate my existing Python application with mimOE.

### Why the OpenAI Python SDK?

mimOE exposes an OpenAI-compatible endpoint, allowing existing SDK patterns to be reused.

### Why `smollm-360m`?

It is lightweight and appropriate for validating local inference and the mimOE integration.

### Why grounded runbooks?

A small model can hallucinate on open-ended technical questions. Supplying trusted context improves reliability.

### Why AWS EC2?

My original Windows desktop had limited free memory. EC2 provided sufficient resources to run the mimOE environment reliably while preserving the same application architecture.

---

## What I Learned

This exercise provided hands-on experience with:

- running LLM inference through mimOE,
- working with an OpenAI-compatible local API,
- integrating a BYO application,
- diagnosing model-loading problems,
- validating AI infrastructure layer by layer,
- dealing with hardware/resource constraints,
- grounding small models with trusted context,
- and designing an AI application around the capabilities and limitations of the selected model.

The most important takeaway was that integrating an AI model is only one part of building an AI application. Runtime reliability, resource management, grounding, observability, configuration, and failure handling are equally important.

---

## Summary

The final solution demonstrates:

```text
mimOE Studio               ✓
mimOE Runtime              ✓
Local model loading        ✓
smollm-360m                ✓
OpenAI-compatible API      ✓
Python BYO agent           ✓
Grounded DevOps runbooks   ✓
Health checking            ✓
Error handling             ✓
Environment configuration ✓
```

The project intentionally remains small and focused so that the mimOE integration and design decisions are easy to understand, reproduce, and explain.
