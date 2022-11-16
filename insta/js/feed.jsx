import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from "react-infinite-scroll-component";
import Post from './post';

class Feed extends React.Component {
  // Show total likes and the like/unlike button for a post
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state  = { jsonPosts: [], nextUrl: "" };
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    
    // Call REST API to get number of likes
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          jsonPosts: data.results,
          nextUrl: data.next,
        });
      })
      .catch((error) => console.log(error));
      
  }

  fetchMoreData(nextPage, posts){
    console.log("IN FETCH ", nextPage);
    
    fetch(nextPage, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          jsonPosts: posts.concat(data.results),
          nextUrl: data.next,
        });
      })
      .catch((error) => console.log(error));

  }

  render() {
      // Render number of likes
      // const likes = []
      // for (const like of this.state.jsonPosts) {
      //     //dont know if next line is right
      //     likes.push(<Post url={like.url} key={like.url}/>)
      // }
      // return (
      //   <div className="feed">
      //     <div>{likes}</div>
      //   </div>
      // );
      const { jsonPosts, nextUrl} = this.state;
      console.log('nextUrl in render: ', nextUrl);
      return (
       

        <InfiniteScroll hasMore dataLength = {this.state.jsonPosts.length} next = {() => this.fetchMoreData(this.state.nextUrl, this.state.jsonPosts)}>
          {
            
            jsonPosts.map((post,idx) => {
              // const { id } = post;
              return (<Post key = {idx} url = {post.url} />);
              })
          }
        </InfiniteScroll>

        
        


      );
      
  }
}
Feed.propTypes = {
    url: PropTypes.string.isRequired,
};

export default Feed;