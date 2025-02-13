# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from typing import Any

import pytest

from datadog_checks.base.stubs.aggregator import AggregatorStub

from .common import CHECK_CONFIG
from .conftest import CONFLUENT_VERSION
from .metrics import ALWAYS_PRESENT_METRICS, CP_62_METRICS, DEPRECATED_METRICS, NOT_ALWAYS_PRESENT_METRICS

# TODO: missing e2e coverage for following metrics. See metrics in metrics.yaml.
#   - Kafka Connect Task Metrics
#   - Kafka Connect Sink Metrics
#   - Kafka Connect Source Tasks Metrics
#   - Kafka Connect Task Error Metrics
#   - Confluent Streams Thread
#   - Confluent Streams Thread Task
#   - Confluent Stream Processor Node Metrics


@pytest.mark.e2e
def test_e2e(dd_agent_check):
    # type: (Any) -> None
    aggregator = dd_agent_check(CHECK_CONFIG, rate=True)  # type: AggregatorStub

    # Skip default `jvm.*` metrics by marking them as asserted
    for metric_name in aggregator._metrics:
        if metric_name.startswith('jvm.'):
            aggregator.assert_metric(metric_name)

    for metric in ALWAYS_PRESENT_METRICS:
        aggregator.assert_metric(metric)

    if CONFLUENT_VERSION == "6.2.0":
        for metric in CP_62_METRICS:
            aggregator.assert_metric(metric)

    if CONFLUENT_VERSION == "5.4.0":
        for metric in DEPRECATED_METRICS:
            aggregator.assert_metric(metric, at_least=0)

    for metric in NOT_ALWAYS_PRESENT_METRICS:
        aggregator.assert_metric(metric, at_least=0)

    aggregator.assert_all_metrics_covered()

    for instance in CHECK_CONFIG['instances']:
        tags = ['instance:confluent_platform-localhost-{}'.format(instance['port']), 'jmx_server:localhost']
        # TODO: Assert the status "status=AgentCheck.OK"
        # JMXFetch is currently sending the service check status as string, but should be number.
        # Add "status=AgentCheck.OK" once that's fixed
        # See https://github.com/DataDog/jmxfetch/pull/287
        aggregator.assert_service_check('confluent.can_connect', tags=tags)
