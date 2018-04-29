# Use the base image.
FROM vision-server-base:latest

RUN mkdir -p /opt/vision

COPY server /opt/vision
COPY ui/dist /opt/vision/dist

COPY docker/server/release/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]