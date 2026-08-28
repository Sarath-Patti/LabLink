# ASP.NET Core 8.0 Runtime Image
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
EXPOSE 5099

ENV ASPNETCORE_URLS=http://+:5099
ENV ASPNETCORE_ENVIRONMENT=Production

# Copy pre-published binaries
COPY dotnet/LabLink.Api/bin/Release/net8.0/publish/ .

ENTRYPOINT ["dotnet", "LabLink.Api.dll"]
