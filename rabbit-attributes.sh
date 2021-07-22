#!/bin/bash
sed -i 's/connection="db"/connection="amqp"/g' ./vendor/magento/module-catalog/etc/queue_consumer.xml
sed -i 's/name="db"/name="amqp"/g' ./vendor/magento/module-catalog/etc/queue_publisher.xml
sed -i 's/connection="db"/connection="amqp"/g' ./vendor/magento/module-catalog/etc/queue_topology.xml
php bin/magento cache:flush;redis-cli -h redis flushall;/usr/share/stratus/cli cache.varnish.clear;/usr/share/stratus/cli cache.cloudfront.invalidate
rm ./rabbit-attributes.sh
echo "Update to product_action_attribute.update & product_action_attribute.website.update for RabbitMQ broker complete, if no errors above"
echo "Please verify that env.php contains correct rabbit creds & product_action_attribute.update & product_action_attribute.website.update consumers, otherwise they will not run"
