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
- [Software Development Kit (SDK)](#software-development-kit-sdk)

## Public API

Our API is hosted at [https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/](https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/)

You can access the interactive documentation at [https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/docs](https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/docs)

You can view the OpenAPI Specification (OAS) file at [https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/openapi.json](https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net/openapi.json)


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

Every push to the `main` branch that includes changes to the `chapter6/` folder automatically:

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


## Software Development Kit (SDK)

*Coming Soon*

Check back for the Python SDK for our API.