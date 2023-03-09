#!/usr/bin/env python3
# Copyright (c) 2016 The Zcash developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.


from test_framework.test_framework import BitcoinTestFramework, ForkHeights
from test_framework.authproxy import JSONRPCException
from test_framework.util import assert_equal, initialize_chain_clean, \
    start_nodes, connect_nodes, wait_and_assert_operationid_status

import sys

RPC_HARD_FORK_DEPRECATION = -40

class ShieldedPoolDeprecationTest (BitcoinTestFramework):

    def setup_chain(self):
        print("Initializing test directory "+self.options.tmpdir)
        initialize_chain_clean(self.options.tmpdir, 2)

    def setup_network(self, split=False):
        args = ['-debug=zrpcunsafe', '-experimentalfeatures', '-zmergetoaddress']
        self.nodes = start_nodes(2, self.options.tmpdir, [['-debug=zrpcunsafe', '-experimentalfeatures', '-zmergetoaddress']] * 2)
        connect_nodes(self.nodes[0],1)
        self.is_network_split=False
        self.sync_all()

    def make_all_mature(self):
        self.sync_all()
        self.nodes[0].generate(1)
        self.sync_all()

    def run_test (self):

        ForkHeight = ForkHeights['SHIELDED_POOL_DEPRECATION']

        print("Mining blocks...")

        self.nodes[0].generate(ForkHeight - 100)
        self.sync_all()

        node0_taddr0 = self.nodes[0].getnewaddress()
        node0_taddr1 = self.nodes[0].getnewaddress()
        node0_taddr2 = self.nodes[0].getnewaddress()
        node0_zaddr0 = self.nodes[0].z_getnewaddress()
        node0_zaddr1 = self.nodes[0].z_getnewaddress()

        # first round pre-fork, second round post-fork
        pre_fork_round = 0
        post_fork_round = 1
        for round in range(2):

            # z_shieldcoinbase

            try:
                # shielding coinbase (multiple times during pre-fork round, the resulting notes will be usefull throughout the test)
                for repeat in range(10 if round == pre_fork_round else 1):
                    opid = self.nodes[0].z_shieldcoinbase(node0_taddr0, node0_zaddr0, 0.0001, 2)["opid"]
                    if (round == post_fork_round):
                        assert(False)
                    wait_and_assert_operationid_status(self.nodes[0], opid)
                    self.make_all_mature()
            except JSONRPCException as e:
                if (round == pre_fork_round):
                    print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                    assert(False)
                else:
                    print("Expected exception caught during testing due to deprecation (error=" + str(e.error["code"]) + ")")
                    assert_equal(e.error["code"], RPC_HARD_FORK_DEPRECATION)

            # z_mergetoaddress

            try:
                # moving transparent funds between node0 t-addresses (before merging)
                self.nodes[0].sendmany("", {node0_taddr1: 1.0, node0_taddr2: 1.0})
                self.make_all_mature()
                # merging transparent funds to z-address (shielding)
                opid = self.nodes[0].z_mergetoaddress(["*"], node0_zaddr0, 0.0001, 2, 2)["opid"]
                if (round == post_fork_round):
                    assert(False)
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                if (round == pre_fork_round):
                    print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                    assert(False)
                else:
                    print("Expected exception caught during testing due to deprecation (error=" + str(e.error["code"]) + ")")
                    assert_equal(e.error["code"], RPC_HARD_FORK_DEPRECATION)

            try:
                # moving transparent funds between node0 t-addresses (before merging)
                self.nodes[0].sendmany("", {node0_taddr1: 1.0, node0_taddr2: 1.0})
                self.make_all_mature()
                # merging transparent funds to z-address (shielding)
                opid = self.nodes[0].z_mergetoaddress(["ANY_TADDR"], node0_zaddr0, 0.0001, 2, 2)["opid"]
                if (round == post_fork_round):
                    assert(False)
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                if (round == pre_fork_round):
                    print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                    assert(False)
                else:
                    print("Expected exception caught during testing due to deprecation (error=" + str(e.error["code"]) + ")")
                    assert_equal(e.error["code"], RPC_HARD_FORK_DEPRECATION)

            try:
                # moving transparent funds between node0 t-addresses (before merging)
                self.nodes[0].sendmany("", {node0_taddr1: 1.0, node0_taddr2: 1.0})
                self.make_all_mature()
                # merging transparent funds to t-address
                opid = self.nodes[0].z_mergetoaddress(["ANY_TADDR"], node0_taddr0, 0.0001, 2, 2)["opid"]
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                    print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                    assert(False)

            try:
                # merging shielded funds to z-address (shielded)
                opid = self.nodes[0].z_mergetoaddress(["ANY_ZADDR"], node0_zaddr0, 0.0001, 2, 2)["opid"]
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                    print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                    assert(False)

            try:
                # merging shielded funds to z-address (unshielding)
                opid = self.nodes[0].z_mergetoaddress(["ANY_ZADDR"], node0_taddr0, 0.0001, 2, 2)["opid"]
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                    print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                    assert(False)

            # z_sendmany

            try:
                # moving transparent funds between node0 t-addresses (before sending to z-address)
                self.nodes[0].sendmany("", {node0_taddr1: 1.0})
                self.make_all_mature()
                # sending transparent funds to z-address (shielding)
                opid = self.nodes[0].z_sendmany(node0_taddr1, [{"address": node0_zaddr0, "amount": 1.0}], 1, 0)
                if (round == post_fork_round):
                    assert(False)
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                if (round == pre_fork_round):
                    print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                    assert(False)
                else:
                    print("Expected exception caught during testing due to deprecation (error=" + str(e.error["code"]) + ")")
                    assert_equal(e.error["code"], RPC_HARD_FORK_DEPRECATION)
            
            try:
                # moving transparent funds between node0 t-addresses (before sending to z-address)
                self.nodes[0].sendmany("", {node0_taddr1: 1.0})
                self.make_all_mature()
                # sending transparent funds to t-address
                opid = self.nodes[0].z_sendmany(node0_taddr1, [{"address": node0_taddr0, "amount": 1.0}], 1, 0)
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                assert(False)

            try:
                # sending shielded funds to z-address (shielded)
                opid = self.nodes[0].z_sendmany(node0_zaddr0, [{"address": node0_zaddr1, "amount": 1.0}], 1, 0)
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                assert(False)

            try:
                # sending shielded funds to z-address (unshielding)
                opid = self.nodes[0].z_sendmany(node0_zaddr0, [{"address": node0_taddr0, "amount": 1.0}], 1, 0)
                wait_and_assert_operationid_status(self.nodes[0], opid)
                self.make_all_mature()
            except JSONRPCException as e:
                print("Unexpected exception caught during testing: " + str(sys.exc_info()[0]))
                assert(False)

            if (round == pre_fork_round):
                blockcount = self.nodes[0].getblockcount()
                if (blockcount < ForkHeight):
                    self.nodes[0].generate(ForkHeight - blockcount)
                    self.sync_all()


if __name__ == '__main__':
    ShieldedPoolDeprecationTest().main()
