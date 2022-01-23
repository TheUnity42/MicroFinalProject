{
  'targets': [
    {
      'target_name': 'effectslib-native',
      'sources': [ 'src/napiBridge.cc', 'src/effectslib.cc', 'src/include/effectslib.hh', 'src/include/effectsBinding.hh', 'src/effectsBinding.cc' ],
      'include_dirs': ["<!@(node -p \"require('node-addon-api').include\")", "<(module_root_dir)/resourses/include/"],
      'dependencies': ["<!(node -p \"require('node-addon-api').gyp\")"],
      'libraries': ['-l"<(module_root_dir)/resources/portaudio_x64.lib"'],
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
