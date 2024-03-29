#!/usr/bin/env python
import os
import subprocess
import shutil
import unittest
import logging
import numpy as np
from test.test_helper import TestHelper, Poller, MessageInFileProbe,\
    ExecutionProbe
from plico.utils.configuration import Configuration
from plico.rpc.zmq_remote_procedure_call import ZmqRemoteProcedureCall
from plico.utils.logger import Logger
from plico.rpc.sockets import Sockets
from plico.rpc.zmq_ports import ZmqPorts
from tipico.client.abstract_instrument_client import SnapshotEntry
from tipico_server.utils.constants import Constants
from tipico_server.utils.starter_script_creator import StarterScriptCreator
from tipico_server.utils.process_startup_helper import ProcessStartUpHelper
from tipico_server.instrument_controller.runner import Runner
from tipico_server.process_monitor.runner import Runner as ProcessMonitorRunner
from tipico.client.instrument_client import \
    InstrumentClient
import sys




class IntegrationTest(unittest.TestCase):

    TEST_DIR= os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           "./tmp/")
    LOG_DIR= os.path.join(TEST_DIR, "log")
    CONF_FILE= 'test/integration/conffiles/tipico_server.conf'
    CALIB_FOLDER= 'test/integration/calib'
    CONF_SECTION= Constants.PROCESS_MONITOR_CONFIG_SECTION
    SERVER_LOG_PATH= os.path.join(LOG_DIR, "%s.log" % CONF_SECTION)
    BIN_DIR= os.path.join(TEST_DIR, "apps", "bin")
    SOURCE_DIR= os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             "../..")


    def setUp(self):
        self._setUpBasicLogging()
        self.server= None
        self._wasSuccessful= False

        self._removeTestFolderIfItExists()
        self._makeTestDir()
        self.configuration= Configuration()
        self.configuration.load(self.CONF_FILE)
        self.rpc= ZmqRemoteProcedureCall()

        calibrationRootDir= self.configuration.calibrationRootDir()
        self._setUpCalibrationTempFolder(calibrationRootDir)


    def _setUpBasicLogging(self):
        logging.basicConfig(level=logging.DEBUG)
        self._logger= Logger.of('Integration Test')


    def _makeTestDir(self):
        os.makedirs(self.TEST_DIR)
        os.makedirs(self.LOG_DIR)
        os.makedirs(self.BIN_DIR)


    def _setUpCalibrationTempFolder(self, calibTempFolder):
        shutil.copytree(self.CALIB_FOLDER,
                        calibTempFolder)


    def _removeTestFolderIfItExists(self):
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)


    def tearDown(self):
        TestHelper.dumpFileToStdout(self.SERVER_LOG_PATH)

        if self.server is not None:
            TestHelper.terminateSubprocess(self.server)

        if self._wasSuccessful:
            self._removeTestFolderIfItExists()


    def _createStarterScripts(self):
        ssc= StarterScriptCreator()
        ssc.setInstallationBinDir(self.BIN_DIR)
        ssc.setPythonPath(self.SOURCE_DIR)
        ssc.setConfigFileDestination(self.CONF_FILE)
        ssc.installExecutables()


    def _startProcesses(self):
        psh= ProcessStartUpHelper()
        serverLog= open(os.path.join(self.LOG_DIR, "server.out"), "wb")
        self.server= subprocess.Popen(
            [sys.executable,
             psh.processProcessMonitorStartUpScriptPath(),
             self.CONF_FILE,
             self.CONF_SECTION],
            stdout=serverLog, stderr=serverLog)
        Poller(5).check(MessageInFileProbe(
            ProcessMonitorRunner.RUNNING_MESSAGE, self.SERVER_LOG_PATH))


    def _testProcessesActuallyStarted(self):
        controllerLogFile= os.path.join(
            self.LOG_DIR,
            '%s.log' % Constants.SERVER_1_CONFIG_SECTION)
        Poller(5).check(MessageInFileProbe(
            Runner.RUNNING_MESSAGE, controllerLogFile))
        controller2LogFile= os.path.join(
            self.LOG_DIR,
            '%s.log' % Constants.SERVER_2_CONFIG_SECTION)
        Poller(5).check(MessageInFileProbe(
            Runner.RUNNING_MESSAGE, controller2LogFile))



    def _buildClients(self):
        ports1= ZmqPorts.fromConfiguration(
            self.configuration, Constants.SERVER_1_CONFIG_SECTION)
        self.instrumentClient1= InstrumentClient(
            self.rpc, Sockets(ports1, self.rpc))
        ports2= ZmqPorts.fromConfiguration(
            self.configuration, Constants.SERVER_2_CONFIG_SECTION)
        self.instrumentClient2= InstrumentClient(
            self.rpc, Sockets(ports2, self.rpc))


    def _testMoveTo(self):
        actuatorPosition= np.arange(10)
        self.instrumentClient1.moveTo(actuatorPosition)
        Poller(3).check(ExecutionProbe(
            lambda: self.assertTrue(
                np.allclose(
                    actuatorPosition,
                    self.instrumentClient1.getPosition()))))


    def _checkBackdoor(self):
        self.instrumentClient1.execute(
            "import numpy as np; "
            "self._myarray= np.array([1, 2])")
        self.assertEqual(
            repr(np.array([1, 2])),
            self.instrumentClient1.eval("self._myarray"))
        self.instrumentClient1.execute("self._foobar= 42")
        self.assertEqual(
            "42",
            self.instrumentClient1.eval("self._foobar"))


    def _testGetStatus(self):
        status= self.instrumentClient1.getStatus()
        cmdCounter= status.commandCounter()
        self.instrumentClient1.moveTo(np.arange(4))
        Poller(3).check(ExecutionProbe(
            lambda: self.assertEqual(
                cmdCounter + 1,
                self.instrumentClient1.getStatus().commandCounter())))


    def _testGetSnapshot(self):
        snapshot= self.instrumentClient1.getSnapshot('aa')
        snKey= 'aa.%s' % SnapshotEntry.SERIAL_NUMBER
        self.assertTrue(snKey in snapshot.keys())


    def _testServerInfo(self):
        serverInfo= self.instrumentClient1.serverInfo()
        self.assertEqual('Server of an instrument',
                         serverInfo.name)
        self.assertEqual('localhost', serverInfo.hostname)


    def testMain(self):
        self._buildClients()
        self._createStarterScripts()
        self._startProcesses()
        self._testProcessesActuallyStarted()
        self._testMoveTo()
        self._testGetStatus()
        self._testGetSnapshot()
        self._testServerInfo()
        self._checkBackdoor()
        self._wasSuccessful= True


if __name__ == "__main__":
    unittest.main()
