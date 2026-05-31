# AI Usage Report

For all tasks described here, I used Claude Code.

## Backend

I implemented the backend code myself and asked AI to write tests.

The prompt: Analyse the /departure endpoint implementation,
and write tests according to requirements: 
1. Queries shorter than 3 characters must return an explicit error
response indicating the input is incomplete. 
2. Return only departures scheduled within the next 15
minutes from “now.” 
3. Stations should be cached. 
4. JSON shapes follow models.

The output was good, but it had some inconsistencies in using mocks in a couple of test cases, which I fixed, and it had some redundant test cases, which I deleted. Also, I added a couple of tests that were missing.

## Frontend

The frontend is mostly implemented by AI.

The prompt: Implement frontend: A search input that triggers a search after the user
types ≥ 3 characters. A clear list or table of departures, grouped or labelled by
station.

It implemented a baseline using styles that are provided when you initialise a React app with Vite, where I changed the UI a bit and added a refresh button. Then I asked to implement tests. The situation was similar to the backend; I deleted some of the test cases and added a couple of them as well.

## Docker setup

I asked Claude Code to write Dockerfiles and a Docker Compose file for reproducibility of the app, and it provided me with a Dockerfile for backend and frontend, an nginx web server config file, and a Docker Compose file. There were some inconsistencies that I fixed: wrong version numbers of Python and Node.js, and it completely ignored variables from .env files and hardcoded them in the Docker Compose file.

## README

I used AI to generate a README with the following sections: Running with Docker, Running locally, Running tests,and Decisions, trade-offs, and known limitations. The sections connected to running were well-written. I just added the command for Windows in one section, which was missing, and added a troubleshooting subsection in the Running with Docker section. The Decisions, trade-offs, and known limitations section I changed a lot.
