{
  'targets': [
    {
      'target_name': 'pa-module-native',
      'sources': [ 'src/pa_module.cc', 'src/effectslib.cc', 'src/include/effectslib.hh' ],
      'include_dirs': ["<!@(node -p \"require('node-addon-api').include\")", "C:\\CLibs\\portaudio\\include", "C:\\CLibs\\portaudio\\build\\msvc\\x64\\Debug"],
      'dependencies': ["<!(node -p \"require('node-addon-api').gyp\")"],
      'libraries': ['-l"C:\\CLibs\\portaudio\\build\\msvc\\x64\\Debug\\portaudio_x64.lib"'],
      'cflags!': [ '-fno-exceptions' ],
      'cflags_cc!': [ '-fno-exceptions' ],
      'xcode_settings': {
        'GCC_ENABLE_CPP_EXCEPTIONS': 'YES',
        'CLANG_CXX_LIBRARY': 'libc++',
        'MACOSX_DEPLOYMENT_TARGET': '10.7'
      },
      'msvs_settings': {
        'VCCLCompilerTool': { 'ExceptionHandling': 1 },
      }
    }
  ]
}
