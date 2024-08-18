import base64
import hashlib
import os

import requests
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from urllib.parse import urlencode, quote_plus
import tweepy



