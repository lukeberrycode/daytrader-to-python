# Builds and runs the unmodified DayTrader 8 from the pinned submodule in legacy/daytrader8.
# Stage 1 builds the WAR with Maven, so nothing needs Java installed locally.
# Stage 2 follows the sample's own Dockerfile.
# The "fixtures" target is the same app with a few prices changed in its database before it starts,
# so rules the shipped data never reaches can be tested (see legacy/docker/fixtures.sql). The code
# is untouched. The default target, built when no --target is given, is the unmodified app.
# Both base images are pinned by digest: the legacy app is the test oracle, so its server and JDK
# change only in a deliberate pull request. The tag says what the digest is; the digest decides.
FROM maven:3.9.16-eclipse-temurin-11@sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64 AS build
WORKDIR /src
COPY daytrader8/ .
RUN mvn -q -B package -DskipTests \
 && mvn -q -B dependency:copy -Dartifact=org.apache.derby:derbytools:10.14.2.0 -DoutputDirectory=/tools

FROM open-liberty:26.0.0.9-full-java8-openj9@sha256:b404d0e0fe3999482cfb75b094483801c39e2dd7b381ed7d68c92b214c0c334f AS legacy
COPY --chown=1001:0 --from=build /src/src/main/liberty/config/server.xml /config/server.xml
COPY --chown=1001:0 --from=build /src/src/main/liberty/config/bootstrap.properties /config/bootstrap.properties
COPY --chown=1001:0 --from=build /src/target/io.openliberty.sample.daytrader8.war /config/apps/
COPY --chown=1001:0 --from=build /src/target/liberty/wlp/usr/shared/resources/DerbyLibs/derby-10.14.2.0.jar /opt/ol/wlp/usr/shared/resources/DerbyLibs/derby-10.14.2.0.jar
COPY --chown=1001:0 --from=build /src/target/liberty/wlp/usr/shared/resources/data /opt/ol/wlp/usr/shared/resources/data
ENV MAX_USERS=1000
ENV MAX_QUOTES=500

FROM legacy AS fixtures
COPY --chown=1001:0 --from=build /tools/derbytools-10.14.2.0.jar /tmp/derbytools.jar
COPY --chown=1001:0 docker/fixtures.sql /tmp/fixtures.sql
RUN java -cp /opt/ol/wlp/usr/shared/resources/DerbyLibs/derby-10.14.2.0.jar:/tmp/derbytools.jar \
      -Dderby.stream.error.file=/tmp/derby.log -Dij.database="jdbc:derby:/opt/ol/wlp/usr/shared/resources/data/tradedb;user=db_username;password=db_password" \
      org.apache.derby.tools.ij /tmp/fixtures.sql \
 && rm /tmp/derbytools.jar /tmp/fixtures.sql /tmp/derby.log

FROM legacy
