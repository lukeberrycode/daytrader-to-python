# Builds and runs the unmodified DayTrader 8 from the pinned submodule in legacy/daytrader8.
# Stage 1 builds the WAR with Maven, so nothing needs Java installed locally.
# Stage 2 follows the sample's own Dockerfile.
FROM maven:3.9-eclipse-temurin-11 AS build
WORKDIR /src
COPY daytrader8/ .
RUN mvn -q -B package -DskipTests

FROM open-liberty:full
COPY --chown=1001:0 --from=build /src/src/main/liberty/config/server.xml /config/server.xml
COPY --chown=1001:0 --from=build /src/src/main/liberty/config/bootstrap.properties /config/bootstrap.properties
COPY --chown=1001:0 --from=build /src/target/io.openliberty.sample.daytrader8.war /config/apps/
COPY --chown=1001:0 --from=build /src/target/liberty/wlp/usr/shared/resources/DerbyLibs/derby-10.14.2.0.jar /opt/ol/wlp/usr/shared/resources/DerbyLibs/derby-10.14.2.0.jar
COPY --chown=1001:0 --from=build /src/target/liberty/wlp/usr/shared/resources/data /opt/ol/wlp/usr/shared/resources/data
ENV MAX_USERS=1000
ENV MAX_QUOTES=500
