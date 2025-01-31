#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/code/catkin_ws/src/dt-core/packages/unicorn_intersection"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/code/catkin_ws/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/code/catkin_ws/install/lib/python3/dist-packages:/code/catkin_ws/build/unicorn_intersection/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/code/catkin_ws/build/unicorn_intersection" \
    "/usr/bin/python3" \
    "/code/catkin_ws/src/dt-core/packages/unicorn_intersection/setup.py" \
     \
    build --build-base "/code/catkin_ws/build/unicorn_intersection" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/code/catkin_ws/install" --install-scripts="/code/catkin_ws/install/bin"
