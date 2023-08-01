import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import moment from 'moment';
import CommentBox from './commentbox';

function Comment(props) {
  const {
    ownerShowUrl, owner, text, lognameOwnsThis, onDelete,
  } = props;
  return (
    <div className="p-1">
      <a href={ownerShowUrl} className="font-weight-bold">{ owner }</a>
      <span> </span>
      <span>{ text }</span>
      <span> </span>
      {lognameOwnsThis ? <button type="button" className="delete-comment-button" onClick={onDelete}>Delete</button> : <div />}
    </div>
  );
}

Comment.propTypes = {
  lognameOwnsThis: PropTypes.bool.isRequired,
  owner: PropTypes.string.isRequired,
  ownerShowUrl: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  onDelete: PropTypes.func.isRequired,
};

function Like(props) {
  const { onClick, text, numLikes } = props;
  return (
    <div className="d-flex flex-column">
      <div>
        <button type="button" className="like-unlike-button" onClick={onClick}>
          {text}
        </button>
      </div>
      <div className="p-1">
        <span>{ numLikes }</span>
        <span>{ numLikes === 1 ? ' like' : ' likes' }</span>
      </div>
    </div>
  );
}

Like.propTypes = {
  numLikes: PropTypes.number.isRequired,
  text: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
};

class Board extends React.Component {
  /* Display number of image and post owner of a single post
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { next: '', results: [], url: '' };
    this.fetchData = this.fetchData.bind(this);
    // console.log("constructor", this.state);
    if (window.performance.getEntriesByType('navigation')[0].type === 'back_forward') {
      this.state = window.history.state;
    }
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    // console.log("componentDidMount", this.state);
    // Call REST API to get the post's information
    const { type } = window.performance.getEntriesByType('navigation')[0];
    if (type !== 'back_forward') {
      fetch(url, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            next: data.next,
            results: data.results,
            url: data.url,
          });
          // console.log("componentDidMount after setState state", this.state);
        })
        .catch((error) => console.log(error));
    }
  }

  handleLikeClick(idx, i) {
    const { state } = this;
    const { results } = state;
    const { postid, likes } = results[idx];
    const { lognameLikesThis, numLikes, url } = likes;
    if (i || !lognameLikesThis) {
      let add = 1;
      let method = 'POST';
      let targeturl = `/api/v1/likes/?postid=${postid}`;
      if (lognameLikesThis) {
        add = -1;
        method = 'DELETE';
        targeturl = url;
      }
      fetch(targeturl, { method, credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          let temp = {};
          if (response.status === 201) {
            temp = response.json();
          }
          return temp;
        })
        .then((data) => {
          // console.log(this.state);
          results[idx].likes.lognameLikesThis = !lognameLikesThis;
          results[idx].likes.numLikes = numLikes + add;
          if (method === 'POST') {
            results[idx].likes.url = data.url;
          } else {
            results[idx].likes.url = null;
          }
          state.results = results;
          this.setState(state);
        })
        .catch((error) => console.log(error));
    }
  }

  handleDeleteComment(idx, cidx, url) {
    fetch(url, { method: 'DELETE', credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        const { state } = this;
        const { results } = state;
        results[idx].comments.splice(cidx, 1);
        state.results = results;
        this.setState(state);
      })
      .catch((error) => console.log(error));
  }

  handleCreateComment(idx, value, event) {
    event.preventDefault();
    const { state } = this;
    const { results } = state;
    const { postid } = results[idx];
    const url = `/api/v1/comments/?postid=${postid}`;
    fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: value }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        results[idx].comments.push(data);
        state.results = results;
        this.setState(state);
      })
      .catch((error) => console.log(error));
  }

  fetchData() {
    // console.log("fetchData", this.state);
    const { next, results } = this.state;
    fetch(next, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          next: data.next,
          results: results.concat(data.results),
          url: data.url,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    // const { imgUrl, owner } = this.state;
    window.history.pushState(this.state, 'pushState');
    // console.log("render", this.state);
    const { next, results } = this.state;
    // Render number of post image and post owner
    return (
      <div className="container px-5">
        <InfiniteScroll
          dataLength={results.length} // This is important field to render the next data
          next={this.fetchData}
          hasMore={next !== ''}
          loader={<h4>Loading...</h4>}
          scrollThreshold={1.0}
        >
          {results.map((res, idx) => {
            // console.log(res, idx);
            const { likes } = res;
            return (
              <div className="border border-secondary mt-5" key={res.postid}>
                <div className="row px-5 py-3  align-items-center">
                  <div className="col">
                    <a href={res.ownerShowUrl} className="align-items-center">
                      <img src={res.ownerImgUrl} width="40" alt={res.ownerImgUrl} />
                      <span>{ res.owner }</span>
                    </a>
                  </div>
                  <div className="col text-right">
                    <a href={res.postShowUrl}>{moment.utc(res.created, 'YYYY-MM-DD hh:mm:ss').fromNow()}</a>
                  </div>
                </div>
                <img src={res.imgUrl} className="w-100" alt={res.imgUrl} onDoubleClick={() => this.handleLikeClick(idx, false)} />
                <div className="d-flex flex-column p-2">
                  <Like numLikes={likes.numLikes} text={(likes.lognameLikesThis ? 'unlike' : 'like')} onClick={() => this.handleLikeClick(idx, true)} />
                  {res.comments.map((comment, cidx) => (
                    <Comment
                      key={comment.commentid}
                      lognameOwnsThis={comment.lognameOwnsThis}
                      owner={comment.owner}
                      ownerShowUrl={comment.ownerShowUrl}
                      text={comment.text}
                      onDelete={() => this.handleDeleteComment(idx, cidx, comment.url)}
                    />
                  ))}
                  <CommentBox
                    handleSubmit={(value, event) => this.handleCreateComment(idx, value, event)}
                  />
                </div>
              </div>
            );
          })}
        </InfiniteScroll>
      </div>
    );
  }
}

Board.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Board;
