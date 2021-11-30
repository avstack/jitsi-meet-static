# jitsi-meet-static: Deploy your Jitsi Meet frontend as a static site

This repository contains a Python script that can compile a Jitsi Meet frontend into static HTML/CSS/JS that can be deployed to any static site host.

This makes it easier to decouple Jitsi Meet's static frontend from the backend components, giving more flexibility for large deployments, and making it easier to use hosted services like [AVStack](https://www.avstack.io/).

This script should work with any relatively recent Jitsi Meet frontend version, and with custom frontends based on any recent Jitsi Meet frontend version. Some modifications may be needed for custom frontends.

## Usage

```
# ./jitsi-meet-static.py --help
usage: jitsi-meet-static.py [-h] --input INPUT --output OUTPUT [--config-url CONFIG_URL] [--interface-config-url INTERFACE_CONFIG_URL] [--stack STACK]

Compile the Jitsi Meet frontend to a static site

options:
  -h, --help            show this help message and exit
  --input INPUT         the path to the checked-out Jitsi Meet source code that will be built
  --output OUTPUT       the destination directory for the compiled static site (which should not already exist)
  --config-url CONFIG_URL
                        a config.js URL, if it should be loaded dynamically rather than baked in
  --interface-config-url INTERFACE_CONFIG_URL
                        an interface_config.js URL, if it should be loaded dynamically rather than baked in
  --stack STACK         an AVStack stack name, as a shortcut for setting --config-url and --interface-config-url
```

## Requirements

* Python 3.
* Node.js and NPM: different Jitsi Meet versions have varying Node.js and NPM requirements for building. The current development code requires Node.js 16 and NPM 8. Previous stable versions required Node.js 14 and NPM 7.

## Example

Build the latest Jitsi Meet stable frontend as a static site, loading its configuration dynamically from an AVStack stack called `teststack` so that it will use that stack as its backend:

**You will need to change the stack name from `teststack` to the name of your own stack for the compiled frontend to work!**) You can get a free 5-user stack at [AVStack](https://www.avstack.io/), or configure your own self-hosted backend instead.

```
# git clone https://github.com/jitsi/jitsi-meet.git
# cd jitsi-meet
# git checkout stable/jitsi-meet_6433
# cd ..

# git clone https://github.com/avstack/jitsi-meet-static.git
# cd jitsi-meet-static
# ./jitsi-meet-static.py --input ../jitsi-meet --output ../out --config-url https://teststack.onavstack.net/config.js --interface-config-url https://teststack.onavstack.net/interface_config.js
# cd ..
```

After running these commands, you have a compiled static Jitsi Meet frontend in the `out` folder. You can upload the content of this folder to any static site host that supports the requirements below.

## Hosting requirements

* HTTPS. Browsers will not allow WebRTC on non-secure origins.
* Must be able to direct non-existent paths matching the conference name format to /index.html. For example, using CloudFront Functions:
  ```js
  function handler(event) {
    var request = event.request;
    if (request.uri.match(/^\/[A-Za-z0-9\/_-]+$/)) {
      request.uri = "/index.html";
    }
    return request;
  }
  ```

## Support

AVStack customers are welcome to contact your AVStack representative for support with this script. Otherwise, please open an issue or pull request!

## License

`jitsi-meet-static` is licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

## Contribution

Any kinds of contributions are welcome as a pull request.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in these crates by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.

## Acknowledgements

`jitsi-meet-static` development is sponsored by [AVStack](https://www.avstack.io/). We provide globally-distributed, scalable, managed Jitsi Meet backends.
