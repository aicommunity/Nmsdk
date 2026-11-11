"""Compiler-argument controls; actual syntax compilation runs on Linux workers."""
import unittest

from ..cpp_syntax_preflight import flags_arguments
from ..native_evidence import EvidenceError


class CppSyntaxPreflightFlagsTest(unittest.TestCase):
    def flags(self, extra='-O3 -DNDEBUG -std=gnu++20'):
        return ('CXX_DEFINES = -DQT_CORE_LIB -DROOT_PATH=\\"/old/source/Bin\\"\n'
                'CXX_INCLUDES = -I/old/source/Rdk/Core -I/old/build/generated -isystem /usr/include/qt5\n'
                'CXX_FLAGS = '+extra+'\n')

    def test_rebases_source_but_keeps_readonly_generated_and_system_headers(self):
        arguments = flags_arguments(self.flags(), '/old/source', '/new/source')
        self.assertIn('-I/new/source/Rdk/Core', arguments)
        self.assertIn('-I/old/build/generated', arguments)
        self.assertIn('/usr/include/qt5', arguments)
        self.assertIn('-DROOT_PATH="/new/source/Bin"', arguments)
        self.assertIn('-std=gnu++20', arguments)

    def test_quoting_is_argument_parsing_and_not_shell_evaluation(self):
        text = self.flags().replace('-I/old/source/Rdk/Core', '-I"/old/source/with spaces"')
        self.assertIn('-I/new/source/with spaces', flags_arguments(text, '/old/source', '/new/source'))

    def test_missing_duplicate_and_make_expansion_fail_before_any_compiler(self):
        for text in (self.flags().replace('CXX_INCLUDES =', 'OTHER ='),
                     self.flags()+'CXX_FLAGS = -g\n', self.flags('$(USER_FLAGS)')):
            with self.subTest(text=text), self.assertRaises(EvidenceError):
                flags_arguments(text, '/old/source', '/new/source')

    def test_write_link_dependency_and_response_options_are_rejected(self):
        for option in ('-o /tmp/result', '-c', '-E', '-S', '-MD', '-MMD', '-MF /tmp/deps',
                       '-save-temps', '@flags.rsp', '-fplugin=plugin.so', '-fprofile-generate'):
            with self.subTest(option=option), self.assertRaises(EvidenceError):
                flags_arguments(self.flags(option), '/old/source', '/new/source')
