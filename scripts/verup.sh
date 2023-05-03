#!/bin/bash
# Increments version git tag or create snapshot version from the release current commit was branched from.
# Saves the version into files listed in VERSION_FILES (space-separated)
# Usage:
#   verup.sh release / feature / branch / ss
# (ss - to create snapshot version)

VERSION_FILES=("src/version.py")

set -u
set -e
set -x

if [[ $(git diff-index HEAD) || $(git status) == *"is ahead"* ]]; then
  echo -e "\n\033[33mPlease commit and push all changes" \
    "before setting version tag\033[39m\n"
  exit -1
fi

if [[ "$1" == "ss" ]]; then
  # get the latest non-snapshot backward from current commit
  TAG=$(git describe --match "[0-9]*" --abbrev=0 || echo "")
else
  # force fetching tags from all branches
  git fetch --tags
  # get the latest by creation, from all branches. note! "[0-9]*" does not repeat square brackets -
  # this is "one digit and any number of any chars".
  TAG=$(git describe --match "[0-9]*.[0-9]*.[0-9]*" --abbrev=0 --tags $(git rev-list --tags --max-count=1) || echo "")
fi

major=0
minor=0
build=0

regex="([0-9]+)\.([0-9]+)\.([0-9]+)"
if [[ $TAG =~ $regex ]]; then
  major="${BASH_REMATCH[1]}"
  minor="${BASH_REMATCH[2]}"
  build="${BASH_REMATCH[3]}"
fi

echo -e "Last version: \033[33m$major.$minor.$build\033[39m"

if [[ "$1" == "release" ]]; then
  build=0
  minor=0
  major=$(echo $major + 1 | bc)
elif [[ "$1" == "feature" ]]; then
  build=0
  minor=$(echo $minor + 1 | bc)
elif [[ "$1" == "bug" ]]; then
  build=$(echo $build + 1 | bc)
elif [[ "$1" == "ss" ]]; then
  major="i$major"
  build="$build-$(git rev-parse --short HEAD)"
else
  echo "usage: ./verup.sh [release|feature|bug|ss]"
  exit -1
fi

NEW_VERSION=$(echo "$major.$minor.$build")
NEW_TAG=$(echo "$NEW_VERSION")  # Tag formatting
echo -e "New version tag: \033[32m$NEW_TAG\033[39m"

read -r -p "Set the version? [y/N] " response
if ! [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  echo "..aborting.."
  exit
fi

for file in ${VERSION_FILES[*]}; do
  echo -e "VERSION = \"$NEW_VERSION\"" >$file
  git add $file
done

COMMIT_MSG=$(git log $TAG..HEAD --format=oneline | awk '{$1=""; print $0}')
COMMIT_MSG=$(echo -e "\n$COMMIT_MSG\n")

echo "Changes:"
echo $COMMIT_MSG
echo

git add $VERSION_FILES
git commit -m "Version $NEW_TAG$COMMIT_MSG"

echo "...push"
git tag $NEW_TAG -m "$COMMIT_MSG"
git push origin $NEW_TAG
git push
