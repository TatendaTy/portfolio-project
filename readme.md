# SportsWorldCentral (SWC) Fantasy Football API Documentation

Thanks for using the SportsWorldCentral API. This is your one-stop shop for accessing data from our fantasy football website, www.sportsworldcentral.com.

## Table of Contents

- [Public API](#public-api)
- [Getting Started](#getting-started)
- [Analytics](#analytics)
- [Player](#player)
- [Scoring](#scoring)
- [Membership](#membership)
- [Terms of Service](#terms-of-service)
- [Example Code](#example-code)
- [Deploying to Azure Cloud](#deploying-to-azure-cloud)
  - [Manual Deployment](#manual-deployment)
  - [Automated Deployment with GitHub Actions](#automated-deployment-with-github-actions)
- [Deploying to Render](#deploying-to-render)
  - [Manual Deployment](#manual-deployment-1)
  - [Automated Deployment with Blueprint](#automated-deployment-with-blueprint)
- [Software Development Kit (SDK)](#software-development-kit-sdk)

## Public API

Our API is deployed on multiple platforms:

**Azure Web App:**
- API: [https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/](https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/)
- Interactive Docs: [https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/docs](https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/docs)
- OpenAPI Spec: [https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/openapi.json](https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/openapi.json)

**Render:**
- API: [https://fantasyfootball-api-service-lmm2.onrender.com](https://fantasyfootball-api-service-lmm2.onrender.com)
- Interactive Docs: [https://fantasyfootball-api-service-lmm2.onrender.com/docs](https://fantasyfootball-api-service-lmm2.onrender.com/docs)
- OpenAPI Spec: [https://fantasyfootball-api-service-lmm2.onrender.com/openapi.json](https://fantasyfootball-api-service-lmm2.onrender.com/openapi.json)


## Getting Started

Since all of the data is public, the SWC API doesn't require any authentication.

All of the the following data is available using GET endpoints that return JSON data.

### Analytics

Get information about the health of the API and counts of leagues, teams, and players.

### Player

You can get a list of all NFL players, or search for an individual player by player_id.

### Scoring

You can get a list of NFL player performances, including the fantasy points they scored using SWC league scoring.

### Membership

Get information about all the SWC fantasy football leagues and the teams in them.

## Terms of Service

By using the API, you agree to the following terms of service:

- **Usage Limits**: You are allowed up to 2000 requests per day. Exceeding this limit may result in your API key being suspended.
- **No Warranty**: We don't provide any warranty of the API or its operation.

## Example Code

Here is some Python example code for accessing the health check endpoint:

```python
import httpx

HEALTH_CHECK_ENDPOINT = "/"

with httpx.Client(base_url=self.swc_base_url) as client:
    response = client.get(self.HEALTH_CHECK_ENDPOINT)
    print(response.json())
```

## Deploying to Azure Cloud

### Manual Deployment

1. **Install the Azure CLI**

   ```bash
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

2. **Login to Azure**

   ```bash
   az login
   ```

3. **Login to Azure Container Registry**

   ```bash
   az acr login --name apicontainerregistry
   ```

4. **Build and tag your Docker image**

   ```bash
   docker build -t azure-api-container:latest .
   docker tag azure-api-container:latest apicontainerregistry.azurecr.io/azure-api-container:latest
   ```

5. **Push the image to ACR**

   ```bash
   docker push apicontainerregistry.azurecr.io/azure-api-container:latest
   ```

6. **Configure the App Service to use the Docker image**

   ```bash
   az webapp config container set \
     --name azure-api-container \
     --resource-group SportsWorldCentral-Fantasy \
     --docker-custom-image-name apicontainerregistry.azurecr.io/azure-api-container:latest \
     --docker-registry-server-url https://apicontainerregistry.azurecr.io
   ```

7. **Restart the web app**

   ```bash
   az webapp restart --name azure-api-container --resource-group SportsWorldCentral-Fantasy
   ```

### Automated Deployment with GitHub Actions

Every push to the `main` branch that includes changes to the `root` folder automatically:

1. Builds a new Docker image
2. Pushes it to Azure Container Registry
3. Deploys to Azure Web App

To manually trigger a deployment:

```bash
git add .
git commit -m "Deploy update"
git push origin main
```

View deployment status in the [GitHub Actions tab](https://github.com/TatendaTy/portfolio-project/actions).

## Deploying to Render

### Manual Deployment

1. **Connect your GitHub repository to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New** → **Web Service**
   - Connect your repository: `TatendaTy/portfolio-project`

2. **Configure the service**
   - **Name**: `fantasyfootball-api-service`
   - **Environment**: `Docker`
   - **Branch**: `main`
   - **Root Directory**: `.`
   - **Dockerfile Path**: `Dockerfile`

3. **Deploy**
   - Click **Create Web Service**
   - Render will build and deploy your container automatically

### Automated Deployment with Blueprint

Using the `render.yaml` file in the root folder:

1. **Create a Blueprint**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New** → **Blueprint**
   - Connect your repository: `TatendaTy/portfolio-project`
   - Render will automatically detect the `render.yaml` file

2. **Review and Apply**
   - Blueprint Name: `SWC API Blueprint`
   - Branch: `main`
   - Click **Apply**

3. **Auto-Deploy**
   - Every push to the `main` branch automatically triggers a new deployment

View your deployment at: [https://fantasyfootball-api-service-lmm2.onrender.com](https://fantasyfootball-api-service-lmm2.onrender.com)

## Software Development Kit (SDK)

If you are a Python user, you can use the SWC SDK to interact with our API.

Install from PyPI:

```bash
python -m pip install swcpy-tydennis0501
```

Quick usage example:

```python
from swcpy import SWCClient, SWCConfig

config = SWCConfig(
   swc_base_url="https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net",
   backoff=False,
)
client = SWCClient(config)
print(client.get_health_check().json())
```

Full SDK documentation is available in [sdk/README.md](sdk/README.md).

