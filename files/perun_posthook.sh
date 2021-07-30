#!/bin/bash
docker stop perun_rpc
docker stop perun_engine
docker stop perun_ldapc
systemctl restart postgresql
systemctl restart slapd
cp /etc/perun/ssl/hostcert.pem /etc/perun/engine/ssl/perun-send.pem
cp /etc/perun/ssl/hostkey.pem /etc/perun/engine/ssl/perun-send.key
cp /etc/perun/ssl/hostchain.pem /etc/perun/engine/ssl/perun-send.chain
docker start perun_rpc
docker start perun_engine
docker start perun_ldapc
docker start perun_apache
docker restart portainer