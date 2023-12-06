* sudo apt install xvfb chromium
* pip3 install selenium
* pip3 install undetected-chromedriver
* pip3 install webdriver-manager
* pip3 install pygame


* add to /etc/ssl/openssl.cnf

```
[openssl_init]
providers = provider_sect

# List of providers to load
[provider_sect]
default = default_sect
legacy = legacy_sect
# The fips section name should match the section name inside the
# included fipsmodule.cnf.
# fips = fips_sect

# If no providers are activated explicitly, the default one is activated implicitly.
# See man 7 OSSL_PROVIDER-default for more details.
#
# If you add a section explicitly activating any other provider(s), you most
# probably need to explicitly activate the default provider, otherwise it
# becomes unavailable in openssl.  As a consequence applications depending on
# OpenSSL may not work correctly which could lead to significant system
# problems including inability to remotely access the system.
[default_sect]
activate = 1

[legacy_sect]
activate = 1
```

