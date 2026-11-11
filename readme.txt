医生分身对齐采样审计台
医疗AI质控团队对医生与分身的成对输出做盲化采样，计算采纳率、覆盖率、修改率和编辑距离并监测时间窗漂移。

测试：python3 -m unittest discover -s tests/avatar_alignment -p 'test_*.py'
构建：python3 -m compileall -q alignment_observatory tests/avatar_alignment
验收：python3 -m alignment_observatory.lab.audit_cli --fixture fixtures/demo.json --database /tmp/avatar_alignment-acceptance.sqlite3
