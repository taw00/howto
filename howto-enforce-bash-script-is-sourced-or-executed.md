# Howto: enforce a bash script to be sourced or directly executed

When we write a bash script we have to take into consideration whether we
intend the script to be sourced or executed.


In short, a "sourced" script ( `source ./myscript.sh` or `. ./myscript.sh` )
will execute the script in the current shell (versus forking a subshell).
Therefore the environment of the current shell instance will be directly
altered. Also, any `exit` commands will log you completely out of the shell.

Alternatively, an "executed" script ( `./myscript.sh` ) will fork to a subshell
and any changes to environment variables within that script will not impact the
current shell you are working in. Similarly, any `exit` command within the
script will only impact the subshell and not the working shell. An executable
script needs to have its execution bit flipped on: `chmod +x ./myscript.sh`.

**Make a decision! Will this script be a sourced script or an executed script?**

Unless the script is a one-off, don't allow the end-user to pick one route or
the other. The behavior is different for each path of execution and it is best
practice to enforce one route or the other.

Enforcement can be achieved with a bit of inquiry at the top of a bash script.
Here are some generic constructs that will give you a clue how things could
work...

```
#!/usr/bin/bash
$(return 0 > /dev/null 2>&1) && echo "this is a sourced script" || echo "this is an executed script"
#$(return 0 > /dev/null 2>&1) && issourced=1 || issourced=0
(( $issourced )) && echo "this is a sourced script" || echo "this is an executed script"
(( $issourced == 1 )) && echo "this is a sourced script" || echo "this is an executed script"
```

...now let's enforce things..


## Enforcing bash script to be _sourced_ not executed

```
#!/usr/bin/bash
$(return 0 > /dev/null 2>&1) || ( echo "please do not run this directly. source it instead." && exit 1 )
```

That `exit` will end the script and `$?` will have a value of that exit code (in this case 1).


## Enforcing bash script to be _executed_ not sourced

```
#!/usr/bin/bash
$(return 0 > /dev/null 2>&1) && echo "please run directly, not as a sourced script" && return 1
```

That `return` will exit but only at the logic scope where it is called. In this
case, the script. If you stick a `return` in a function, for example, it will
only exit that function and the script will continue otherwise. This is a
primary reason why "sourcing" instead of "executing" can have unexpected
execution behaviors.

Leaving that scope, `$?` will be set to the return value.

