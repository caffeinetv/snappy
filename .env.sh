# Snappy environment shell import

function usage() {
  echo "Usage: $0 -e ENV"
  echo "Where ENV is either: "
  echo "  devtest"
  echo "  production"
  echo "e.g. $0 -e production"
  exit 1
}


# Validate CLI arguments
if [ "$1" != "-e" ]; then
  echo "ERROR: Missing -e CLI argument."
  usage
fi

case "$2" in
  devtest)
    ;;
  production)
    ;;
  *)
    echo "ERROR: Unknown environment \"$2\"."
    usage
esac


# If we made it this far, CLI arguments are valid
export SERVERLESS_ENV=$2
