# Coding Challenge: Digital Assistant Service

## Overview
A Java Spring Boot service that allows an user to perform two tasks:
1. Define a name and text response string for a digital assistant.
2. Send a text message to the named assistant and receive the defined string.

## Technologies
- Java 21
- Spring Boot 3.5.0
- Maven 3.9.9
- IntelliJ IDEA

## Getting Started

### Prerequisites
- JDK 21+

### Run

```bash
# Run the app
java -jar digitalassistant-0.0.1-SNAPSHOT.jar

The application will start on:
http://localhost:8080

Base URL for API requests:
http://localhost:8080/api/assistant

1. Register a new assistant:
   - Method: POST
   - URL: http://localhost:8080/api/assistant/register
   - Body: 
     ```json
     {
       "name": "AssistantName",
       "response": "Hello, I am your digital assistant!"
     }
     ```
2. Send a message to the registered assistant based on its name:
    - Method: GET
    - URL: http://localhost:8080/api/assistant/message/AssistantName
```
