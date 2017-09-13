from argparse import ArgumentParser
from os import environ
from os.path import join, dirname, abspath, isfile
from subprocess import call

from dotenv import load_dotenv
from clint.textui import colored


parser = ArgumentParser(description="QProb DevOps")
parser.add_argument('--cron')
parser.add_argument('--nginx')
args = parser.parse_args()

BASE_DIR = dirname(dirname(abspath(__file__)))
load_dotenv(join(BASE_DIR, '.env'))
host = environ.get("HOST")
api_port = environ.get("API_PORT")


def cron_writer(proj: str, template: str) -> None:
    assert isinstance(proj, str), "Project name should be string"
    assert isinstance(template, str), "Template should be string"

    with open(join(BASE_DIR, "scripts", "templates", "{0}.tpl".format(template)), 'r') as tpl:
        cfg = tpl.read()

        with open('/home/{0}/{1}.sh'.format(proj, template), 'w') as f:
            f.write(cfg.format(proj))
            print(colored.green("Wrote cron script for {}.".format(proj)))


def nginx_writer(proj: str, template: str) -> None:
    #FIXME assert doesn't recognize striing
    #assert isinstance(proj, str), "Project name should be string"
    assert isinstance(template, str), "Template should be string"

    with open(join(BASE_DIR, "scripts", "templates", "{0}.tpl".format(template)), 'r') as tpl:
        cfg = tpl.read()

        assert isinstance(host, str), "Host should be string"
        assert isinstance(api_port, str), "Port should be string"

        with open('/etc/nginx/sites-enabled/{0}.conf'.format(proj), 'w') as f:
            f.write(cfg.format(proj, host, api_port))
            print(colored.green("Wrote nginx script for {}.".format(proj)))


def install_nginx():
    call(["sudo", "apt", "install", "nginx", "-y"])


def reload_nginx():
    call(["service", "nginx", "reload"])


def generate_cert(name: str, domain: str) -> None:
    #TODO maybe check for renewals
    if not isfile("/etc/letsencrypt/live/{0}/fullchain.pem".format(domain)):
        call(["/usr/local/sbin/certbot-auto", "certonly", "--webroot", "-w", "/home/{0}".format(name), "-d", "{0}".format(host)])
    if not isfile("/etc/letsencrypt/live/www..{0}/fullchain.pem".format(domain)):
        call(["/usr/local/sbin/certbot-auto", "certonly", "--webroot", "-w", "/home/{0}".format(name), "-d", "ww.{0}".format(host)])
    if not isfile("/etc/letsencrypt/live/api.{0}/fullchain.pem".format(domain)):
        call(["/usr/local/sbin/certbot-auto", "certonly", "--webroot", "-w", "/home/{0}/api".format(name), "-d", "api.{0}".format(host)])


def write_nginx_main():
    with open(join(dirname(__file__), "templates", "nginx_maain.tpl"), 'r') as tpl:
        cfg = tpl.read()

        with open('/etc/nginx/nginx.conf', 'w') as f:
            f.write(cfg)
            print(colored.green("Wrote Nginx config file."))


def main():
    if not args.cron is None:
        cron_writer(proj=args.cron, template="cron")
        cron_writer(proj=args.cron, template="week_cron")
    if not args.nginx is None:
        if args.nginx == "w":
            write_nginx_main()
        if args.nginx == "r":
            reload_nginx()
        if not args.nginx in ["r", "w"]:
            if not isfile("/etc/letsencrypt/live/{0}/fullchain.pem".format(host)):
                nginx_writer(proj=args.nginx, template="nginx_nossl")
                reload_nginx()
                generate_cert(name=args.nginx, domain=host)
            nginx_writer(proj=args.nginx, template="nginx")
            reload_nginx()


main()