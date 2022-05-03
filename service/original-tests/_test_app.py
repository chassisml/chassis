#!/usr/bin/env python
# -*- coding utf-8 -*-

import pytest

def test_alive(client):
    assert client.get('/').status_code == 200

#  def test_get_job_status_api_no_authorization(client):
    #  assert client.get('/job/fake').status_code == 401
