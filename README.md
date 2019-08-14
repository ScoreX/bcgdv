# Implementation notes

- Each service is implemented as its own docker container
- Orchestration is done via docker-compose
- Services
    - web: nginx frontend
    - storage: image storage and retrieval
    - rotate: image rotation
    - filter: image filters e.g blur, sharpen
- progimage package contains a client library for interacting with the service


# Running

- Edit docker-compose.yml to add  AWS IAM credentials with S3 access to the storage service
- docker-compose build
- docker-compose up

