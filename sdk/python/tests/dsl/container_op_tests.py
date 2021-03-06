# Copyright 2018-2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
from kubernetes.client.models import V1EnvVar, V1VolumeMount

from kfp.dsl import Pipeline, PipelineParam, ContainerOp, Sidecar


class TestContainerOp(unittest.TestCase):

  def test_basic(self):
    """Test basic usage."""
    with Pipeline('somename') as p:
      param1 = PipelineParam('param1')
      param2 = PipelineParam('param2')
      op1 = (ContainerOp(name='op1', image='image',
          arguments=['%s hello %s %s' % (param1, param2, param1)],
          sidecars=[Sidecar(name='sidecar0', image='image0')],
          container_kwargs={'env': [V1EnvVar(name='env1', value='value1')]},
          file_outputs={'out1': '/tmp/b'})
            .add_sidecar(Sidecar(name='sidecar1', image='image1'))
            .add_sidecar(Sidecar(name='sidecar2', image='image2')))
      
    self.assertCountEqual([x.name for x in op1.inputs], ['param1', 'param2'])
    self.assertCountEqual(list(op1.outputs.keys()), ['out1'])
    self.assertCountEqual([x.op_name for x in op1.outputs.values()], ['op1'])
    self.assertEqual(op1.output.name, 'out1')
    self.assertCountEqual([sidecar.name for sidecar in op1.sidecars], ['sidecar0', 'sidecar1', 'sidecar2'])
    self.assertCountEqual([sidecar.image for sidecar in op1.sidecars], ['image0', 'image1', 'image2'])
    self.assertCountEqual([env.name for env in op1.container.env], ['env1'])

  def test_after_op(self):
    """Test duplicate ops."""
    with Pipeline('somename') as p:
      op1 = ContainerOp(name='op1', image='image')
      op2 = ContainerOp(name='op2', image='image')
      op2.after(op1)
    self.assertCountEqual(op2.dependent_names, [op1.name])


  def test_deprecation_warnings(self):
    """Test deprecation warnings."""
    with Pipeline('somename') as p:
      op = ContainerOp(name='op1', image='image')

    with self.assertWarns(PendingDeprecationWarning):
      op.env_variables = [V1EnvVar(name="foo", value="bar")]

    with self.assertWarns(PendingDeprecationWarning):
      op.image = 'image2'

    with self.assertWarns(PendingDeprecationWarning):
      op.set_memory_request('10M')

    with self.assertWarns(PendingDeprecationWarning):
      op.set_memory_limit('10M')

    with self.assertWarns(PendingDeprecationWarning):
      op.set_cpu_request('100m')

    with self.assertWarns(PendingDeprecationWarning):
      op.set_cpu_limit('1')

    with self.assertWarns(PendingDeprecationWarning):
      op.set_gpu_limit('1')

    with self.assertWarns(PendingDeprecationWarning):
      op.add_env_variable(V1EnvVar(name="foo", value="bar"))

    with self.assertWarns(PendingDeprecationWarning):
      op.add_volume_mount(V1VolumeMount(
        mount_path='/secret/gcp-credentials',
        name='gcp-credentials'))
