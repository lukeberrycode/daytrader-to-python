# Apache JMeter 5.6.3 for the NFR-1 load baseline, from the official Apache archive, plus the
# WebSocket Samplers plugin DayTrader's scripts need (Maven Central). Both are checked against
# their published SHA-512 checksums. The JRE image is pinned by digest.
FROM eclipse-temurin:21.0.12.1_1-jre-noble@sha256:35501d3f93173b420ac9001658eb68157e813316b865087e345c187fca422c4c
ARG JMETER=apache-jmeter-5.6.3
ARG SHA512=5978a1a35edb5a7d428e270564ff49d2b1b257a65e17a759d259a9283fc17093e522fe46f474a043864aea6910683486340706d745fcdf3db1505fd71e689083
ARG WS=jmeter-websocket-samplers-1.3.2
ARG WS_SHA512=e0a8d5b898868d66815703aa36f573815592735d4b0e175d749c27ed5096150e28fa59266cdf3ba04b4f654e28859f7eae9a6afbab33c3998c68be29c7d1e559
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends curl >/dev/null \
 && curl -fsSL -o /tmp/jmeter.tgz https://archive.apache.org/dist/jmeter/binaries/${JMETER}.tgz \
 && echo "${SHA512}  /tmp/jmeter.tgz" | sha512sum -c - \
 && tar -xzf /tmp/jmeter.tgz -C /opt && rm /tmp/jmeter.tgz \
 && curl -fsSL -o /opt/${JMETER}/lib/ext/${WS}.jar \
      https://repo1.maven.org/maven2/net/luminis/jmeter/jmeter-websocket-samplers/1.3.2/${WS}.jar \
 && echo "${WS_SHA512}  /opt/${JMETER}/lib/ext/${WS}.jar" | sha512sum -c - \
 && rm -rf /var/lib/apt/lists/*
ENV PATH="/opt/${JMETER}/bin:${PATH}"
ENTRYPOINT ["jmeter"]
