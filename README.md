# Rate Limit using python and Redis

## How to run ?

1.  Create Virtualenv and activate

```
    virtualenv RateLimitPython
    cd RateLimitPython
    source bin/activate
```

2. Install requirements

```
    pip install -r requirements.txt
```

3. Run docker container

```
    docker-compose -f src/docker-compose.yml up -d
```

4. Run the file

```
    python3 src/rate_limit.py
```

# Note:

This is used for Proof Of Concept and not meant to be used in production.
