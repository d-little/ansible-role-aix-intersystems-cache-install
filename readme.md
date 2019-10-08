# ansible-role-aix-intersystems-cache-install

**This readme is under heavy construction.  The Role itself is done, but this readme needs some work!**

## How to Use

- Download Intersystems Cache distro and place in `{{ cache_install.local_files_dir }}` (default: `./files/`)
- Assumes you have a working Yum configuration (requires rsync)
- Uses [Cache Install parameters](https://cedocs.intersystems.com/latest/csp/docbook/DocBook.UI.Page.cls?KEY=GCI_unix#GCI_unix_install_unattended)
- Templates and uses a [Cache Installation Manifest](https://cedocs.intersystems.com/latest/csp/docbook/DocBook.UI.Page.cls?KEY=GCI_manifest) file

## Variables and Manfiest Settings

### cache_install

#### cache_install defaults

The default `cache_install` settings are as follows:

```yaml
cache_install:
  version: ''   # Must be 'full' release number, as found in the cache-{{version}}.tar.gz file
                # eg: cache-2018.1.2.309.5-ppc64.tar.gz
  local_files_dir: "files/"  # Local ansible directory where the cache tar.gz files live
  temp_dir: /tmp/cache/  # Directory on target host that install files should be stored  
  target_dir: /usr/cachesys/  # Where to install the Cache instance
  instance_name: cache
  ccontrol: ccontrol
  csession: csession
  cache_key_file:
  users:
  parameters:
    # Only required parameters have set defaults.
    #  'Suggested Defaults' can be used with the {{ cache_install_use_recommended }} flag
    ISC_PACKAGE_INSTANCENAME: cache
    ISC_PACKAGE_INSTALLDIR: /usr/cachesys/
    ISC_INSTALLER_MANIFEST:
    ISC_INSTALLER_LOGFILE: installer_log
    ISC_INSTALLER_LOGLEVEL: 3
```

#### cache_install_use_recommended

You can enable the variable `cache_install_use_recommended` in your vars files to enable the following additional defaults:

```yaml
__cache_install_user_uid: 10077
__cache_install_recomended:
  # A collection of settings I think 'should' be set
  users:
    root: root
    owner:
      name: cacheusr
      uid: "{{ __cache_install_user_uid }}"
      # group: cacheusr - Will use cache_install.users.group_allowed.name
    effective_user:
      name: cacheusr
      uid: "{{ __cache_install_user_uid }}"
      group: cacheusr
    effective_group:
      name: cacheusr
      gid: "{{ __cache_install_user_uid }}"
    group_allowed:
      name: cacheusr
      gid: "{{ __cache_install_user_uid }}"
  parameters:
    ISC_PACKAGE_STARTCACHE: 'N'
    ISC_PACKAGE_MGRUSER: cacheusr
    ISC_PACKAGE_MGRGROUP: cacheusr
```

### Cache_Install_Manifest*

#### Merging Behaviour ('deep_combine')

Our yaml for the Manifest has been designed in such a way that you can have multiple definitions in multiple vars files and they'll all merge together.  To do this everything in the Manifest is indexed by `Name`, and the role will run a lookup for all Ansible variables that start with `Cache_Install_Manifest*`.  These will then all be recusively merged together in alphabetical order.

ie:

```yaml
Cache_Install_Manifest_Site1:
  SystemSettings:
    setting1: value1
    setting2: value2

Cache_Install_Manifest_Site2:
  SystemSettings:
    setting3: value3
    dict1:
      d1: v1
      d2: v2

Cache_Install_Manifest_Site3:
  SystemSettings:
    setting1: overwritevalue1
    dict1:
      d2: anothervalue
```

These three will become merged as:

```yaml
Cache_Install_Manifest:
  SystemSettings:
    setting1: overwritevalue1
    setting2: value2
    setting3: value3
    dict1:
      d1: v1
      d2: anothervalue
```

We dont define what goes in each field, you do that;  we simply render everything supplied.  It's up to the user to ensure that they supply valid tags/values.  See [the documentation](https://cedocs.intersystems.com/latest/csp/docbook/DocBook.UI.Page.cls?KEY=GCI_manifest#GCI_manifest_tags) for valid manifest tags.

NB:

- You can define databases at both the Manifest and Namespace Configuration levels... **Should we just pull out databases and just have it in Manifest?**
- If you leave Code/Data empty on a Namespace definition, it will assume that the Database for those given options are the same as the Namespace name.

#### Full Configuration Eample

Example vars file contents:

```yaml
---
cache_install_user_group_uid: 1300
cache_install:
  version: 2018.1.2.309.5
  temp_dir: "/tmp/binaries/cache/"
  users:
    owner:
      name: cacheusr
      uid: "{{ cache_install_user_group_uid }}"
    effective_user:
      name: cacheusr
      uid: "{{ cache_install_user_group_uid }}"
      group: cacheusr
    effective_group:
      name: cacheusr
      gid: "{{ cache_install_user_group_uid }}"
    group_allowed:
      name: cacheusr
      gid: "{{ cache_install_user_group_uid }}"

Cache_Install_Manifest_SystemSOE:
  SystemSettings:
    Config.config.wijdir: /jnl/wij/
    Config.Journal.CurrentDirectory: /jnl/jnla/
    Config.Journal.AlternateDirectory: /jnl/jnlb/
    Config.Journal.FreezeOnError: 1
    Config.Journal.DaysBeforePurge: 7
    Config.Journal.BackupsBeforePurge: 0
  Users:  
    Someone:
      Roles: '%ALL'
      Fullname: Test Account
      Namespace: '%SYS'
      ChangePassword: 1
      Enabled: 1
      Comment: Test Account Creation
  Databases:
    SYSDATABASE:
      Dir: /db/system/sysdatabase/
    APPDATABASE:
      Dir: /db/system/appdatabase/
    APPDEVGROUP1:
      Dir: /db/system/appdevgroup1/
    APPDEVGROUP2:
      Dir: /db/system/appdevgroup2/
    VERSIONCONTROL:
      Dir: /db/system/versioncontrol/
    UTL:
      Dir: /db/system/utl/
    BUSINESS1:
      Dir: /db/business1/
    BUSINESS2:
      Dir: /db/business2/
  Namespaces:
    SYSDATABASE:
    APPDATABASE:
    APPDEVGROUP2:
    VERSIONCONTROL:
    UTL:
    APPDEVGROUP1:
    BUSINESS1:
      Code: APPDATABASE
    BUSINESS2:
      Code: APPDATABASE
    '%ALL':
      Code: SYSDATABASE
      Data: SYSDATABASE
      Configuration:
        GlobalMappings:
          'Z*': { From: SYSDATABASE }
          'vc*': { From: VERSIONCONTROL }
          'z*': { From: SYSDATABASE }
          'TEMP': { From: CACHETEMP }
          'Temp': { From: CACHETEMP }
          'temp': { From: CACHETEMP }
          'wk*': { From: CACHETEMP }
          'WK*': { From: CACHETEMP }
        RoutineMappings:
          '%Z*': { From: APPDATABASE }
          '%vc*': { From: VERSIONCONTROL }
          '%z*': { From: APPDATABASE }
        ClassMappings:
          Utility: { From: UTL }
          VerControl: { From: VERSIONCONTROL }
```
